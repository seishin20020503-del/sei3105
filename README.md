# FrameStep

写真ライブラリから動画を選び、1コマずつ／2コマおき／3コマおきにフレーム送りして確認できる iOS アプリです。

## 主な機能

- `PHPickerViewController` でライブラリから動画を1本選択（フォトライブラリの許可ダイアログは不要）
- 選んだ動画を `AVAssetImageGenerator`（許容誤差ゼロ）でフレーム単位の静止画として正確に表示
- 「1コマ」「2コマおき」「3コマおき」を切り替えられるステップ幅ピッカー
- 前後のコマ送りボタン、スライダーでの直接シーク、通常再生（AVPlayer によるライブプレビュー）
- フレーム番号 / 総フレーム数の表示

## 構成

```
FrameStep/
  FrameStep.xcodeproj/        # Xcodeプロジェクト（iOS 17.0+、SwiftUI）
  FrameStep/
    FrameStepApp.swift        # アプリのエントリーポイント
    ContentView.swift         # 動画選択画面
    VideoPicker.swift         # PHPickerViewController のラッパー
    FramePlayerViewModel.swift# フレーム精度の再生/ステップ制御ロジック
    FramePlayerView.swift     # フレームプレイヤーのUI
    Assets.xcassets/          # AppIcon / AccentColor（プレースホルダー）
    Preview Content/
```

## ビルド方法

1. macOS + Xcode 15 以降で `FrameStep/FrameStep.xcodeproj` を開く
2. シミュレータまたは実機を選択して実行（実機テストには動画ファイルが必要です）

## App Store 提出前に必要な作業（このリポジトリには含まれていません）

- Apple Developer Program のアカウントと証明書/プロビジョニングプロファイル
- `Assets.xcassets/AppIcon.appiconset` への実際のアプリアイコン画像（1024x1024）
- `PRODUCT_BUNDLE_IDENTIFIER`（現在は仮の `com.framestep.app`）を自分のチームのIDに変更
- App Store Connect 上でのアプリ登録、スクリーンショット、説明文、プライバシー情報の入力
- 実機での動作確認（大きい動画/長時間動画でのパフォーマンス確認を推奨）

これらはApple Developerアカウントでの操作が必要なため、コード側の実装のみを用意しています。
