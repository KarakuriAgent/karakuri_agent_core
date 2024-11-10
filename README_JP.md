# からくりエージェント

Karakuri Agentは、2D画像を用いたAIとのインタラクティブなコミュニケーションを実現するクロスプラットフォームアプリケーションです。

## 対応プラットフォーム

| プラットフォーム | 対応状況 |
|----------------|:--------:|
| Android        |    ❌    |
| iOS            |    ❌    |
| Web            |    🟢    |
| macOS          |    ❌    |
| Linux          |    ❌    |
| Windows        |    ❌    |

## 対応サービスとエンドポイント

| サービス        | エンドポイント | 対応状況 |
|----------------|----------------|:--------:|
| OpenAI         | text           |    🟢    |
|                | text to speech |    🟢    |
|                | speech to text |    🟢    |
| VoiceVox       | text to speech |    🟢    |
| StyleBertVITS2 | text to speech |    ❌    |

## Quick Start
[![Open in IDX](https://cdn.idx.dev/btn/open_purple_32.svg)](https://idx.google.com/import?url=https://github.com/0235-jp/karakuri_agent)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/0235-jp/karakuri_agent)

## 開発環境のセットアップ
Flutter環境があれば開発可能です。
https://docs.flutter.dev/get-started/install

Docker composeで簡単にセットアップも可能です。

### Dockerのインストール
```
curl -L https://get.docker.com | sh
```

### sudoを使用せずに Docker コマンドを実行するには、現在のユーザーを Docker グループに追加します。

#### ユーザーが誰であるかわからない場合は、次のコマンドを実行して現在のユーザーを確認してください。
```
whoami
```

#### 次のコマンドを実行します。$USERを、上記のコマンドを実行して得られた結果に置き換えます。
```
sudo usermod -aG docker $USER
sudo reboot
```

### 次のコマンドでイメージを立ち上げることができ、Visual Studio Codeの開発コンテナ等でアクセスするとローカル環境と同様に開発ができます。
```
docker compose -f compose-dev.yml up -d
```
## コマンド例
ここでは例としてWebのビルド及びサーバーの起動の方法をきしします。各プラットフォームのビルド等は各自コマンドを変更して実行してください。

### プロジェクトの初期化
```
dart run rps get default

// for web
dart run rps get web
```

### ビルドランナーの実行
言語ファイル等を生成します。
```
dart run rps gen
```

### Webサーバーの起動
```
dart run rps run-release web
```

### Webのビルド
/buildに出力されます。
```
dart run rps build-release web
```

### Docker Composeの使用
以下のコマンドを使用して、Docker環境でWebサーバーを起動できます。
```
docker compose -f compose-server.yml up -d
```
