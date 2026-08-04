# wp-auto-post

WordPRESS の REST API を使って、Claude Code から記事を投稿するためのCLIツールです。
明成個別学習指導塾サイト（meiseikobetsu.jp）の「マイブログ」機能で使うことを想定していますが、
実体は標準の WordPress 投稿 API なので、通常の投稿権限があればどのサイトでも使えます。

## できること

- タイトル・本文（Markdown or HTML）を指定して記事を作成（デフォルトは**下書き保存**）
- カテゴリー・タグを名前で指定（存在しなければ自動作成）
- アイキャッチ画像のアップロード＆設定
- 公開日時の指定（予約投稿）
- `--status publish --yes` を明示したときだけ即時公開（誤って一般公開しない安全策）

## セットアップ

### 1. 依存パッケージのインストール

```bash
npm install
```

### 2. アプリケーションパスワードの発行

1. WordPress管理画面で「ユーザー」→「あなたのプロフィール」を開く
2. ページ下部の「アプリケーションパスワード」欄に名前（例: `Claude Code 自動投稿`）を入力し発行
3. 表示されたパスワード（スペース区切りの英数字）をコピー

ログインパスワードそのものではなくこの専用パスワードを使うので、不要になったらプロフィール画面からいつでも無効化できます。

### 3. `.env` を作成

```bash
cp .env.example .env
```

`.env` を開いて以下を設定してください。

```
WP_URL=https://meiseikobetsu.jp
WP_USERNAME=あなたのログインID
WP_APP_PASSWORD=発行したアプリケーションパスワード
```

`.env` は `.gitignore` 済みなので、リポジトリにはコミットされません。

### 4. 接続確認

```bash
node src/cli.js whoami
```

`接続成功: 小原 陸 (id=..., roles=...)` のように表示されれば成功です。

## 使い方

### 手動で記事を投稿する（下書き保存 → 管理画面で確認 → 公開）

```bash
node src/cli.js post \
  --title "【2027年度】〇〇高校入試情報" \
  --content-file article.md \
  --category "高校入試情報" \
  --tag "2027年度" --tag "浦和"
```

実行後に表示される編集画面URLを開いて内容を確認し、問題なければ管理画面から「公開」してください。

### 本文をその場で指定する

```bash
node src/cli.js post --title "テスト投稿" --content "本文をここに書きます"
```

### 標準入力から本文を渡す（Claude Codeに記事を書かせてそのまま投稿する場合など）

```bash
cat article.md | node src/cli.js post --title "自動生成記事" --category "お知らせ"
```

### 内容を確認済みで、その場で公開したい場合

```bash
node src/cli.js post --title "本日のお知らせ" --content "本文" --status publish --yes
```

`--yes` を付けずに `--status publish` を指定すると、確認なしの誤公開を防ぐためにエラーで止まります。

### アイキャッチ画像を設定する

```bash
node src/cli.js post --title "..." --content-file article.md --featured-image ./eyecatch.jpg
```

### オプション一覧

| オプション | 説明 |
|---|---|
| `--title` | 記事タイトル（必須） |
| `--content` | 本文をその場で指定（Markdown） |
| `--content-file` | 本文ファイルのパス |
| `--format markdown\|html` | 本文の形式（デフォルト: markdown） |
| `--status draft\|publish\|pending` | 投稿ステータス（デフォルト: draft） |
| `--category <name>` | カテゴリー名（複数指定可、存在しなければ自動作成） |
| `--tag <name>` | タグ名（複数指定可、存在しなければ自動作成） |
| `--featured-image <path>` | アイキャッチ画像ファイル |
| `--excerpt <text>` | 抜粋 |
| `--date <ISO8601>` | 公開日時（予約投稿） |
| `--yes` | `--status publish` を確認なしで実行する |

## Claude Code に「記事を書いて投稿して」と頼む

このツールはCLIなので、Claude Codeとのチャットで

> ○○高校の2027年度入試情報について記事を書いて、カテゴリー「高校入試情報」で下書き保存して

のように頼めば、Claude Codeが本文を作成し、このCLIを呼び出して下書き保存まで行います。
内容の正確性（募集人員・内申点・面接の配点など）は必ず人の目で確認してから公開してください。

## 定期的に自動投稿したい場合（スケジュール実行）

このリポジトリ自体には常駐のスケジューラは含めていません。Claude Codeの「Routine」（定期実行の仕組み）を使うことで、
「毎週月曜9時に○○について記事を書いて下書き保存する」といった定期実行が可能です。Claude Codeに

> 毎週月曜9時に、△△について記事を書いてこのツールで下書き保存するように設定して

と頼んでください。安全のため、自動実行では `--status draft`（下書き保存まで）を既定にし、公開は人が確認してから行うことを推奨します。

## 注意事項

- WordPressのREST APIが無効化されているサイトやセキュリティプラグインでAPIをブロックしている場合は動作しません。
- アプリケーションパスワードは第三者に知られないよう `.env` の取り扱いに注意してください。
- 入試情報など事実関係が重要な記事は、自動生成した内容をそのまま公開せず、必ずレビューを挟んでください。
