# maimai-motion

maimai（SEGAのタッチパネル音楽ゲーム）のプレイ動画から手の動きを解析し、
改善点を列挙するCLIツールです。MediaPipe Handsで手のランドマークを検出し、

- **手の移動効率**: タッチ間の実際の軌道が最短経路に対してどれだけ無駄に長いか
- **タイミングのズレ**: 譜面（ノーツ時刻）データを与えた場合、検出したタッチとのズレ（早押し/遅れ）

をMarkdownレポートとして出力します。

## セットアップ

```bash
pip install -e .
```

依存パッケージ: `opencv-python`, `mediapipe`, `matplotlib`

## 使い方

```bash
maimai-motion path/to/gameplay.mp4 --out report.md
```

譜面データ（ノーツ時刻）を使ったタイミング分析も行う場合:

```bash
maimai-motion path/to/gameplay.mp4 --chart examples/sample_chart.json --out report.md
```

軌道の可視化プロットを保存する場合:

```bash
maimai-motion path/to/gameplay.mp4 --plot-left left.png --plot-right right.png
```

### 主なオプション

| オプション | 説明 | デフォルト |
| --- | --- | --- |
| `--chart PATH` | タイミング分析用のJSON譜面ファイル | なし（移動効率のみ解析） |
| `--landmark N` | 追跡に使うMediaPipeランドマーク番号（0=手首, 8=人差し指先） | `0` |
| `--speed-threshold V` | この速度(px/秒)以下を「静止＝タッチ」とみなす | `40.0` |
| `--timing-window S` | タッチとノーツを対応付ける最大時間差(秒) | `0.5` |
| `--timing-ok S` | このズレ(秒)以内は「良好」とみなす | `0.05` |
| `--mirror` | 左右の手ラベルを入れ替える（カメラ視点による） | オフ |
| `--top-n N` | レポートに載せる上位件数 | `5` |

`--speed-threshold` はカメラの解像度・距離によって最適値が変わるため、
最初は生成されたレポートを見ながら調整してください。

### 譜面JSONフォーマット

simai/maidata形式ではなく、シンプルな独自フォーマットです（`examples/sample_chart.json` 参照）。

```json
[
  {"time": 1.0, "hand": "left", "label": "tap"},
  {"time": 1.5, "hand": "right"}
]
```

- `time`: 動画開始からのノーツ時刻（秒）
- `hand`: `"left"` / `"right"` / `"either"`（省略時は `"either"`）
- `label`: レポートに表示する任意のラベル（省略可）

## 制限事項・注意点

- カメラは手元（タッチパネル）が正面から見える角度で撮影してください。斜めや遠景では検出精度が落ちます。
- MediaPipeの左右判定はカメラの向きに依存します。レポートの左右が逆に見える場合は `--mirror` を試してください。
- タイミング分析には別途、動画の開始時刻を基準にしたノーツ時刻データが必要です（現時点では譜面ファイルからの自動生成は非対応）。
- タッチ検出は「手の停止＝タッチ」という近似です。素早いタップが連続する場面では検出漏れ・誤検出が起こり得ます。

## 開発

```bash
pip install -e ".[dev]"
pytest
```

`tests/` にはMediaPipe/OpenCVに依存しないコアロジック（タッチ検出・効率計算・
譜面照合・レポート生成）のユニットテストがあります。動画入出力部分
（`hand_tracker.py`）は実際の動画ファイルでの手動確認を想定しています。
