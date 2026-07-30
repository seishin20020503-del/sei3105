# Macなしで実機にインストールする方法(App Store・サイドローディング)

XcodeはmacOS専用ですが、「ビルドはGitHubのクラウドMacに任せて、インストールはWindows PCの無料ツールで行う」ことで、
Macを一切持たずにFrameStepを自分のiPhoneで動かせます。Apple IDやパスワードはあなたのPC上のツールにしか入力せず、
このリポジトリやGitHub Actionsには一切渡りません。

## 全体の流れ

1. GitHub Actionsで（無料の）macOSビルド環境を使い、署名なしの`.ipa`を作る
2. Windows PC上の**Sideloadly**(または**AltStore/AltServer**)で、そのipaに自分の無料Apple IDで署名してiPhoneにインストール

## 手順1: GitHub Actionsでビルドする

このリポジトリには `.github/workflows/build-unsigned-ipa.yml` を追加済みです。

1. GitHub上でこのリポジトリを開く
2. 「Actions」タブ → 左側の「Build Unsigned IPA」を選択
3. 「Run workflow」ボタンを押して実行(ブランチは `claude/ios-video-filter-frame-player-2oco2w` を指定)
4. 数分待つと実行が完了するので、実行結果画面の一番下「Artifacts」から `FrameStep-unsigned-ipa` をダウンロード
5. 中身の `FrameStep-unsigned.ipa` を取り出しておく

GitHubの無料枠(Freeプラン: 月2000分、macOSランナーは10倍消費なので実質約200分相当)の範囲で収まるはずです。
非公開リポジトリでActionsの無料枠を使い切っている場合のみ、追加の課金が発生する可能性があります。

## 手順2: Sideloadlyでインストールする(Windows / macOS対応)

1. Windows PCに [Sideloadly](https://sideloadly.io/) をインストール
2. iPhoneをUSBでPCに接続し、iTunesまたはApple Devicesアプリを一度入れてドライバを認識させておく
3. Sideloadlyを起動し、手順1でダウンロードした `FrameStep-unsigned.ipa` をウィンドウにドラッグ&ドロップ
4. Apple ID欄に自分の無料のApple IDとパスワードを入力(2段階認証がある場合はアプリ用パスワードが必要になることがあります)
5. 「Start」を押すと、Sideloadlyが自動で署名してiPhoneにインストールします
6. iPhone側で「設定 → 一般 → VPNとデバイス管理」を開き、自分のApple IDの開発者アプリを「信頼」する

## 注意点

- **7日で失効します**: 無料Apple IDでの署名は7日間しか有効ではありません。期限が切れるとアプリが起動しなくなるので、
  再度Sideloadlyでインストールし直してください(手順1のipaファイルは使い回せます)。
- **AltStore/AltServerという選択肢**もあります。こちらはPCとiPhoneが同じWi-Fiにさえ繋がっていれば自動で
  再署名してくれる機能があり、7日ごとの手動作業が面倒な場合はこちらの方が楽です(仕組みはSideloadlyとほぼ同じです)。
- Apple IDのパスワードは、これらのサードパーティ製ツール(Sideloadly/AltServer)に直接入力する形になります。
  公式ツールではないため、利用は自己責任になりますが、iOSサイドローディング用として広く使われている定番ツールです。
- コードに変更を加えて試したい場合は、リポジトリを更新するたびに手順1のGitHub Actionsを再実行してipaを作り直してください。
