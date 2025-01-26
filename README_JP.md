# 🤖 からくりエージェント

「**からくりエージェント**」は、あらゆる環境（スマートスピーカー、チャットツール、Webアプリなど）からアクセス可能な **AIエージェント** を目指したオープンソースプロジェクトです。  
多種多様なエンドポイントやサービスとの統合により、**1つのエージェント** へ **どこからでもアクセス可能** な世界を実現します。  
複数のエージェントを同時に定義し、それぞれに異なる役割・性格・音声・モデルを割り当てることも可能です。

## 技術概要

### 🚀 **サーバーサイド**:
- フレームワーク: FastAPI
- メモリ管理: Zep

### 🪶 **モデル対応 (LLM)**: 
LiteLLMを利用し、[LiteLLM](https://github.com/BerriAI/litellm)がサポートしているモデル(例: OpenAI, Ollama)にアクセス可能。  
- **OpenAIモデル利用の例**: [OpenAI APIキー](https://platform.openai.com/) を取得し、`.env`にAPIキーやモデルを設定してください。  
- **Ollamaモデル利用の例**: [Ollama](https://docs.ollama.ai/)をローカルで起動し、そのURLを`.env`に設定することで利用可能になります。

### 🎙️ **音声合成(TTS)**

| Service | Support Status |
| - | - |
| Voicevox Engine | 🟢 対応済 |
| AivisSpeech Engine | 🟢 対応済 |
| にじボイスAPI | 🟢 対応済 |
| OpenAI | ❌ 未対応(将来対応予定) |
| Style-Bert-VITS2 | ❌ 未対応(将来対応予定) |

**VoicevoxEngineの設定例**:  
VoicevoxEngineはローカルで稼働させる必要があります。  
[公式ドキュメント](https://github.com/VOICEVOX/voicevox_engine)に従いVoicevoxEngineを起動し、  
そのエンドポイント（例: `http://localhost:50021`）を `.env` ファイルの `AGENT_1_TTS_BASE_URL` に指定してください。

### 🎧 **音声認識(STT)**

| Service | Support Status |
| - | - |
| faster-whisper | 🟢 対応済 |
| OpenAI Whisper | ❌ 未対応(将来対応予定) |

`faster-whisper`はPythonライブラリを通じて動作しますが、特別な外部サービス起動は不要です。（`requirements.txt`をインストールすることで利用可能になります）

### **エンドポイント** 

| Endpoint        | Support Status             |
|-----------------|----------------------------|
| text to text    | 🟢 対応済                  |
| text to voice   | 🟢 対応済                  |
| text to video   | ❌ 未対応(将来対応予定)   |
| voice to text   | 🟢 対応済                  |
| voice to voice  | 🟢 対応済                  |
| voice to video  | ❌ 未対応(将来対応予定)   |
| video to text   | ❌ 未対応(将来対応予定)   |
| video to voice  | ❌ 未対応(将来対応予定)   |
| video to video  | ❌ 未対応(将来対応予定)   |
| OpenAI Chat API | 🟢 対応済 (エージェントIDをモデル名として使用) |

### **サービス統合**

| Service | Support Status             |
|---------|----------------------------|
| LINE    | 🟢 対応済                  |
| Slack   | ❌ 未対応(将来対応予定)   |
| Discord | ❌ 未対応(将来対応予定)   |

※ 未対応機能・サービスについては、[Projectタブ](https://github.com/0235-jp/karakuri_agent/projects)や[Discussions](https://github.com/0235-jp/karakuri_agent/discussions)で開発状況・ロードマップをご確認ください。

## ⚡ 特徴

- **幅広いエンドポイント対応**  
  - 📝 Text to Text  
  - 💬 Text to Voice  
  - 🎤 Voice to Text 
  - 🔄 Voice to Voice

- **長期記憶システム**
  - 🧠 永続的な会話履歴
  - 👤 ユーザーごとのコンテキスト管理
  - 📝 セッションベースのメモリ管理
  - 🌐 セルフホストZepとZep Cloudの両対応
  - 🔍 関連情報の抽出とコンテキスト強化
  - 🔎 高度なメモリ検索機能
    - ファクトとメモリノードの検索
    - セマンティック検索の統合
    - コンテキストを考慮した情報検索
  - ⚡ Valkeyキャッシュによるパフォーマンス最適化
    - セッションメモリのキャッシング
    - セッション間のコンテキスト保持

- **ユーザー管理機能**
  - 👥 ユーザーの登録・削除
  - 📊 ユーザー情報の取得
  - 📋 ユーザー一覧の表示

- **モデル選択の柔軟性**  
  LiteLLMを用いているため、LiteLLMがサポートしているモデル (例: OpenAI, Ollama) に対応可能。

- **複数エージェント管理**  
  `.env` で複数エージェントを定義可能。役割や性格、音声プロファイルなどを自由に設定できます。

- **サービス連携**  
  現在は **LINE** に対応。将来的には他のメッセージングサービスや音声インターフェースとの連携も予定。

## 🎥 デモ・スクリーンショット

*開発中のため、後日更新予定！*  
Flutterクライアントの画面や音声インタラクションのGIFを公開予定です。

## 📦 環境要件

- **サーバーサイド**  
  - Python 3.8以上  
  - (任意) VoicevoxEngine (TTS用)  
    - ローカルでVoicevoxEngineを起動し、  
    - そのエンドポイント（例: `http://localhost:50021`）を `.env` ファイルの `AGENT_1_TTS_BASE_URL` に指定してください  
  - (任意) LINE連携を利用する場合は、[LINE Developer Console](https://developers.line.biz/ja/)よりトークン・シークレット取得が必要

- **各種LLMサービスモデル利用時**  
  - 有効なAPIキーおよびインターネット接続が必要。

- **Ollamaモデル利用時**  
  - Ollamaをローカルで起動する必要があります。

## 🛠️ インストール方法

### Docker Composeを利用する場合

プロジェクトルートにある`compose.yml`を使用すると、  
サーバーをコンテナで一括起動できます。

```bash
docker compose up
```

上記コマンドで`http://localhost:8080` でサーバーが起動します。

`.env`は事前に設定しておいてください。

### サーバーサイドのセットアップ(手動)

1. `.env`ファイルの作成、及び必要に応じて修正
   ```bash
   cp example.env .env
   ```
   `.env`でエージェント数やモデル設定、APIキーなどを設定します。
   
2. 必要なパッケージインストール  
   ```bash
   pip install -r requirements.txt
   ```
3. サーバー起動  
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
   ```
   → `http://localhost:8080` でFastAPIサーバーが起動します。

## 💡 使い方

- Swagger UIでAPIのフォーマットを確認および実行  
  `http://localhost:8080/docs`

## ⚙️ 設定・カスタマイズ

`.env` や環境変数で設定可能です。例:  
```
API_KEYS=サーバーアクセス用のAPIキーをカンマ区切りで指定
LINE_MAX_AUDIO_FILES=LINE統合で利用する音声ファイルの最大保存件数 (例:5)
LINE_AUDIO_FILES_DIR=line_audio_files
CHAT_MAX_AUDIO_FILES=Chatエンドポイントで利用する音声ファイルの最大保存件数 (例:5)
CHAT_AUDIO_FILES_DIR=chat_audio_files
WEB_SOCKET_MAX_AUDIO_FILES=WebSocketエンドポイントで利用する音声ファイルの最大保存件数 (例:5)
WEB_SOCKET_AUDIO_FILES_DIR=websocket_audio_files

AGENT_1_NAME=エージェントの名前
AGENT_1_MESSAGE_GENERATE_LLM_BASE_URL=メッセージ生成用LLMのURL(LiteLLM形式)
AGENT_1_MESSAGE_GENERATE_LLM_API_KEY=メッセージ生成用LLMのAPIキー
AGENT_1_MESSAGE_GENERATE_LLM_MODEL=メッセージ生成用LLMのモデル(LiteLLM形式)
AGENT_1_EMOTION_GENERATE_LLM_BASE_URL=表情生成用LLMのURL(LiteLLM形式)
AGENT_1_EMOTION_GENERATE_LLM_API_KEY=表情生成用LLMのAPIキー
AGENT_1_EMOTION_GENERATE_LLM_MODEL=表情生成用LLMのモデル(LiteLLM形式)
AGENT_1_VISION_GENERATE_LLM_BASE_URL=画像認識用LLMのURL(LiteLLM形式)※メッセージ生成用LLMが画像に非対応な場合に利用
AGENT_1_VISION_GENERATE_LLM_API_KEY=画像認識用LLMのAPIキー
AGENT_1_VISION_GENERATE_LLM_MODEL=画像認識用LLMのモデル(LiteLLM形式)
AGENT_1_TTS_TYPE=利用するTTSのタイプ(対応Type:voicevox,nijivoice(AivisSpeechもvoicevoxを指定ください。))
AGENT_1_TTS_BASE_URL=TTSエンドポイントのURL
AGENT_1_TTS_API_KEY=TTSのAPIキー(なければ空白で問題有りません)
AGENT_1_TTS_SPEAKER_MODEL=TTSのモデル(対応モデル:default)
AGENT_1_TTS_SPEAKER_ID=TTSのスピーカーID
AGENT_1_LLM_SYSTEM_PROMPT=エージェントに設定するシステムプロンプト
AGENT_1_LINE_CHANNEL_SECRET=LINEチャンネルシークレット(LINE統合を利用する場合は必要)
AGENT_1_LINE_CHANNEL_ACCESS_TOKEN=LINEチャンネルアクセストークン(LINE統合を利用する場合は必要)
AGENT_1_ZEP_URL=エージェント1用のZepサーバーURL
AGENT_1_ZEP_API_SECRET=エージェント1用のZep APIシークレットキー

# AGENT_2_... と接頭辞を増やすことで、複数エージェントが定義可能
```

## 🤝 コントリビュート方法

1. Issueでバグ報告・改善提案を歓迎します！  
2. `main`ブランチから作業用ブランチを作成し、Pull Requestをお送りください。  
3. 機能提案や質問は[Discussions](https://github.com/0235-jp/karakuri_agent/discussions)でも受け付けています。

## 📜 ライセンスについて

本プロジェクトは独自のライセンス規約に基づいています。

- **非商用利用**: 個人による学習・研究・趣味目的などの非商用利用は無料で可能です。改変物を再配布する場合は、著作権表示と本ライセンス全文を保持してください。
- **商用利用**: 本ソフトウェアまたはその改変物を用いて収益を得る、商業的目的での利用には、事前に株式会社0235との商用ライセンス契約が必要です。
不明な点や商用利用のライセンス取得については、[karakuri-agent-support@0235.co.jp](mailto:karakuri-agent-support@0235.co.jp) までお問い合わせください。

詳細は [LICENSE](LICENSE_JP) ファイルをご確認ください。

## 🛠️ 構築・運用サポート

本プロジェクトの構築・運用に関する有償でのサポートも承ります。料金は要件に応じてお見積りとなりますので、詳細は [karakuri-agent-support@0235.co.jp](mailto:karakuri-agent-support@0235.co.jp) までお問い合わせください。

## 🔗 関連プロジェクト・参考資料

- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)  
- [Flutter公式ドキュメント](https://docs.flutter.dev/)  
- [LINE Messaging API](https://developers.line.biz/ja/docs/messaging-api/)  
- [LiteLLM](https://github.com/BerriAI/litellm)  
- [Voicevox Engine](https://github.com/VOICEVOX/voicevox_engine)  
- [AivisSpeech Engine](https://github.com/Aivis-Project/AivisSpeech-Engine)  
- [Style-Bert-VITS2](https://github.com/litagin02/Style-Bert-VITS2)  
- [faster-whisper](https://github.com/guillaumekln/faster-whisper)  
- [OpenAI Whisper](https://github.com/openai/whisper)  
- [Ollama](https://docs.ollama.ai/)
- [にじボイスAPIドキュメント](https://docs.nijivoice.com/docs/getting-started)
