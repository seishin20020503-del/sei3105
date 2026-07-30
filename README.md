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

## App Store 公開手順

具体的な手順は [`APP_STORE_SUBMISSION.md`](./APP_STORE_SUBMISSION.md) にまとめています。
アプリ説明文などの下書きは [`APP_STORE_METADATA.md`](./APP_STORE_METADATA.md)、
プライバシーポリシーの下書きは [`PRIVACY_POLICY.md`](./PRIVACY_POLICY.md) を参照してください。

Apple Developer Programへの登録、Xcodeでの署名・アーカイブ・アップロード、App Store Connectでの
審査提出は、Apple IDでの認証や金銭・法的手続きを伴うためご自身のMacで実行する必要があります。
