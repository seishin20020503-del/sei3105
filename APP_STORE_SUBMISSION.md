# App Store 公開手順（FrameStep / ネイティブXcodeプロジェクト版）

参考記事（Zenn「Claude Codeで1日でアプリを作ってApp Store公開」）はExpo + EAS Build/Submitの手順でしたが、
FrameStepはSwift/SwiftUIのネイティブXcodeプロジェクトなので、EASコマンドは使わず、Xcode + App Store Connectで
同じ流れ（Phase 3: 公開準備 → Phase 4: ビルド・申請）を進めます。

**注意**: ここから先はApple Developerアカウントでのログイン、Xcodeの実行、macOS環境が必須です。
このセッション（Linuxのサンドボックス環境）からは実行できないため、以下はすべてご自身のMacで行ってください。
コード側でできる部分（プロジェクト設定、プライバシーポリシー文面、メタデータ文面、アプリアイコン）はこのリポジトリに用意済みです。

## Phase 3 相当: 公開準備

### 1. Apple Developer Programへの登録
- https://developer.apple.com/programs/ から登録（年額 $99）
- 個人 or 組織のいずれかを選択して手続き（本人確認に数日かかる場合があります）

### 2. Bundle IDの確定
- 現在プロジェクトの`PRODUCT_BUNDLE_IDENTIFIER`は仮の`com.framestep.app`になっています
  (`FrameStep/FrameStep.xcodeproj/project.pbxproj`内、Debug/Release両方)
- 自分のチームで使う一意なIDに変更してください（例: `com.yourname.framestep`）
- Xcodeで開いて「FrameStep」ターゲット → General → Bundle Identifier を書き換えるのが簡単です
- 併せて「Signing & Capabilities」で自分のApple Developerチームを選択（Automatic signingのままでOK）

### 3. App Store Connectで新規アプリを登録
- https://appstoreconnect.apple.com/ → マイApp → 「+」→ 新規App
- プラットフォーム: iOS
- 名前・プライマリ言語・Bundle ID（上で決めたもの）・SKUを入力

### 4. アプリアイコン
- `FrameStep/FrameStep/Assets.xcassets/AppIcon.appiconset/` に1024x1024のプレースホルダーアイコンを
  生成済みで配置してあります（`AppIcon-1024.png`）。そのまま使ってもよいですし、正式公開前に
  デザインを差し替えても構いません（差し替える場合も1024x1024・アルファチャンネルなしのPNGにしてください）。

### 5. プライバシーポリシー
- `PRIVACY_POLICY.md` に下書きを用意しました。GitHub Pagesなど任意の場所でHTML/Markdownとして公開し、
  そのURLをApp Store Connectの「プライバシーポリシーURL」欄に設定してください。
- 「お問い合わせ」欄のメールアドレスはご自身のものに書き換えてください。

### 6. アプリ説明文・キーワード・カテゴリなど
- `APP_STORE_METADATA.md` に、アプリ名/サブタイトル/説明文/キーワード/カテゴリ/年齢制限の下書きを
  用意しました。App Store Connectの該当項目にコピーして調整してください。

### 7. スクリーンショット
- Xcodeでシミュレータ（例: iPhone 16 Pro Max）を起動してFrameStepを実行し、Cmd+Sでスクリーンショットを保存
- 動画選択画面／フレームプレイヤー画面／コマ送り幅ピッカー操作中、の3カットを撮ると分かりやすいです
- これは実機/シミュレータでアプリが動いている状態が必要なため、このセッションでは用意できません

## Phase 4 相当: ビルド・申請

### 1. 実機/シミュレータで最終動作確認
- Xcodeで実行し、動画選択→コマ送り→再生の一連の流れを確認してください
- 特に、iOSの画面録画のような可変フレームレート動画でコマ送りが正確に動くかも確認してください

### 2. アーカイブ作成
- Xcode上部の実行先を「Any iOS Device (arm64)」に切り替え
- メニュー: Product → Archive

### 3. App Store Connectへアップロード
- アーカイブ完了後に開くOrganizerウィンドウで「Distribute App」→「App Store Connect」→「Upload」を選択
- 署名は自動（Automatically manage signing）でOK
- アップロード後、処理完了まで数分〜数十分かかります（App Store Connect上の「TestFlight」やビルド一覧に反映されます）

### 4. 審査提出
- App Store Connectの対象アプリ画面で、アップロードしたビルドを選択
- スクリーンショット・説明文・プライバシーポリシーURL・年齢制限などの入力を完了させる
- 「審査へ提出（Submit for Review）」をクリック

### 5. 審査結果を待つ
- 通常1〜3日程度でApple側の審査結果（承認 or リジェクト）が通知されます
- リジェクトされた場合は理由を確認し、修正して再提出してください

---

このリポジトリで用意済みのもの: Xcodeプロジェクト一式、フレーム精度ロジック、アプリアイコン(プレースホルダー)、
プライバシーポリシー下書き、App Store説明文/メタデータ下書き。
ここから先（Apple Developer登録、Xcodeでのビルド・署名・アップロード、App Store Connectでの申請）は、
Apple IDでの認証や実際の金銭・法的手続きを伴うため、必ずご自身の手で実行してください。
