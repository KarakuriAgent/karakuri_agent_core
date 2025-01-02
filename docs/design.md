# からくりエージェント 設計書

## 1. プロジェクト概要

からくりエージェントは、複数の環境（スマートスピーカー、チャットツール、Webアプリなど）から利用可能なAIエージェントを実現するためのオープンソースプロジェクトです。

### 1.1 主な特徴

- マルチエンドポイント対応（Text/Voice/Video）
- 複数エージェント管理
- 柔軟なLLMモデル選択
- 音声合成(TTS)・音声認識(STT)対応
- 各種サービス連携（LINE等）

## 2. システムアーキテクチャ

### 2.1 全体構成

```
app/
├── api/            # APIエンドポイント
│   └── v1/         # APIバージョン1
├── auth/           # 認証関連
├── core/           # コアロジック
├── schemas/        # データモデル
└── utils/          # ユーティリティ
```

### 2.2 主要コンポーネント

#### 2.2.1 APIエンドポイント (/api/v1/)
- chat.py: テキスト/音声チャット
- line.py: LINE Messaging API連携
- agents.py: エージェント管理
- web_socket.py: WebSocket通信

#### 2.2.2 コアサービス (/core/)
- agent_manager.py: エージェント設定・管理
- llm_service.py: LLMサービス連携
- tts_service.py: 音声合成サービス
- stt_service.py: 音声認識サービス
- memory_service.py: 会話履歴管理
- config.py: 環境設定管理

#### 2.2.3 認証 (/auth/)
- api_key.py: APIキー認証

## 3. 機能詳細

### 3.1 エージェント管理システム

エージェントは環境変数で定義され、以下の要素を含みます：
- 基本情報（ID、名前）
- LLM設定（メッセージ生成、感情生成、画像認識）
- TTS設定（エンドポイント、話者ID等）
- サービス連携設定（LINEチャンネル等）

### 3.2 対応エンドポイント

| エンドポイント | 状態 | 説明 |
|--------------|------|------|
| text to text | ✅ | テキスト入力からテキスト応答 |
| text to voice | ✅ | テキスト入力から音声応答 |
| voice to text | ✅ | 音声入力からテキスト応答 |
| voice to voice | ✅ | 音声入力から音声応答 |

### 3.3 エージェントの状態管理

#### 3.3.0 APIエンドポイント

| エンドポイント | メソッド | 説明 |
|--------------|---------|------|
| `/v1/agents/{agent_id}/status` | GET | エージェントの現在のステータスを取得 |
| `/v1/agents/{agent_id}/status` | PUT | エージェントのステータスを更新 |
| `/v1/agents/{agent_id}/schedule` | GET | エージェントの当日のスケジュールを取得 |
| `/v1/agents/{agent_id}/availability` | GET | 各コミュニケーションチャンネルの利用可否を取得 |

リクエスト・レスポンス例：

```json
// GET /v1/agents/1/status
{
    "current_status": "available",
    "last_status_change": "2024-01-01T12:00:00",
    "next_status_change": "2024-01-01T22:00:00",
    "status_message": "通常対応可能です"
}

// PUT /v1/agents/1/status
Request:
"working"

Response:
{
    "current_status": "working",
    "last_status_change": "2024-01-01T13:00:00",
    "next_status_change": null,
    "status_message": "作業中ですが、チャットでの対応は可能です"
}

// GET /v1/agents/1/schedule
{
    "date": "2024-01-01",
    "items": [
        {
            "start_time": "08:00",
            "end_time": "12:00",
            "activity": "通常業務",
            "status": "available",
            "description": "メールチェックと一般的な問い合わせ対応",
            "location": "オフィス"
        },
        {
            "start_time": "12:00",
            "end_time": "13:00",
            "activity": "昼食",
            "status": "eating",
            "description": "昼食休憩",
            "location": "カフェテリア"
        }
    ],
    "generated_at": "2024-01-01T07:30:00",
    "last_updated": "2024-01-01T07:30:00"
}

// GET /v1/agents/1/availability
{
    "chat": true,
    "voice": false,
    "video": false
}
```
#### 3.3.1 ステータスと利用可能なコミュニケーション
```python
class CommunicationChannel(str, Enum):
    CHAT = "chat"          # Text-based communication (LINE, etc.)
    VOICE = "voice"        # Voice communication
    VIDEO = "video"        # Video communication (for future expansion)

class AgentStatus(str, Enum):
    AVAILABLE = "available"     # Free and ready to interact
    SLEEPING = "sleeping"       # Currently sleeping
    EATING = "eating"          # Having a meal
    WORKING = "working"        # Working on tasks but can handle chat
    OUT = "out"               # Outside/Away but can handle chat
    MAINTENANCE = "maintenance" # System maintenance mode
```

各ステータスでのコミュニケーション可否：
| ステータス | チャット | 音声 | ビデオ |
|-----------|---------|------|--------|
| AVAILABLE | ✅ | ✅ | ✅ |
| SLEEPING | ❌ | ❌ | ❌ |
| EATING | ✅ | ❌ | ❌ |
| WORKING | ✅ | ❌ | ❌ |
| OUT | ✅ | ❌ | ❌ |
| MAINTENANCE | ❌ | ❌ | ❌ |

#### 3.3.2 スケジュール管理
- 起床30分前に自動的に当日のスケジュールを生成
- LLMを使用した動的なスケジュール作成
- エージェントの性格や役割に基づいた活動の設定

スケジュールデータ構造：
```python
class ScheduleItem(BaseModel):
    start_time: str
    end_time: str
    activity: str
    status: AgentStatus
    description: Optional[str]
    location: Optional[str]

class DailySchedule(BaseModel):
    date: date
    items: List[ScheduleItem]
    generated_at: datetime
    last_updated: datetime
```

#### 3.3.3 状態に応じた応答生成
- LLMを使用した文脈に応じた応答の生成
- 現在の状態、スケジュール、次の利用可能時間を考慮
- エージェントの性格に合わせた応答スタイル

応答生成の考慮要素：
- 現在時刻
- 現在のステータス
- 現在の活動内容
- 場所情報
- 次の利用可能時間
- ユーザーのメッセージ内容
- エージェントのキャラクター設定

### 3.4 外部サービス連携

#### 3.4.1 LLM (Language Models)
- LiteLLM対応モデル

#### 3.4.2 TTS (Text-to-Speech)
- Voicevox Engine
- AivisSpeech Engine
- にじボイスAPI

#### 3.4.3 STT (Speech-to-Text)
- faster-whisper

#### 3.4.4 メッセージングプラットフォーム
- LINE

## 4. データフロー

### 4.1 基本的な処理フロー

1. クライアントからのリクエスト受信
2. APIキー認証
3. エージェント設定の読み込み
4. 現在のステータスと利用可能性の確認
   - 利用不可の場合：状況に応じた応答を生成
   - 利用可能な場合：通常の処理を継続
5. 入力形式に応じた前処理
   - テキスト: そのまま処理
   - 音声: STTで変換
   - 画像: Vision LLMで解析
6. LLMによるメッセージ生成
   - 現在の状態とスケジュールを考慮
   - エージェントの性格に基づいた応答生成
7. 感情生成（必要な場合）
8. 出力形式に応じた後処理
   - テキスト: そのまま返信
   - 音声: TTSで変換
9. レスポンス送信

### 4.2 スケジュール管理フロー

1. スケジュール生成トリガー（起床30分前）
2. エージェント情報の取得
   - 基本設定
   - 性格設定
   - 定期的なスケジュール
3. LLMによるスケジュール生成
   - エージェントの特性を考慮
   - 必要な活動の組み込み
   - 適切な時間配分
4. スケジュールの検証
   - 時間の整合性チェック
   - 必須活動の確認
5. スケジュールの保存
   - キャッシュへの保存
   - 必要に応じた更新

### 4.2 メモリ管理

- Redisを使用した会話履歴の管理
- 設定可能なトークン使用量の閾値
- 自動的な古い履歴の削除

### 4.3 メモリサービス詳細

#### 4.3.1 会話履歴管理
- データ構造
  ```python
  # キー: conversation_history:{agent_id}
  [
    {
      "role": "user/assistant/system",
      "content": "メッセージ内容"
    }
  ]
  ```
- トークン数管理
  - LiteLLMのtoken_counterを使用したトークン数計算
  - モデルごとのmax_input_tokensに基づく閾値設定
    ```python
    max_tokens = model_cost[model]["max_input_tokens"] or 8192
    threshold = int(max_tokens * threshold_tokens_percentage)  # デフォルト0.8
    ```
  - 閾値超過時の古いメッセージの削除ロジック
    - 最初のユーザーメッセージから次のユーザーメッセージまでを削除

#### 4.3.2 Redisデータモデル
- キー設計
  - 会話履歴: `conversation_history:{agent_id}`
- 同時実行制御
  - asyncio.Lockによる排他制御
  - 会話履歴の更新時にロックを使用
- 実装詳細
  - redis.asyncio非同期クライアントの使用
  - JSON形式でのデータシリアライズ

### 4.4 エラーハンドリング

#### 4.4.1 サービス別エラー対応
- LLMサービス
  - 接続エラー: 最大3回のリトライ
  - レート制限: 指数バックオフによる再試行
  - モデル不使用時: 代替モデルへのフォールバック
- TTS/STTサービス
  - 音声合成エラー: テキスト応答へのフォールバック
  - 音声認識エラー: ユーザーへの再入力リクエスト
- 外部API（LINE等）
  - 一時的な接続エラー: キューイングと再試行
  - 認証エラー: 管理者への通知

#### 4.4.2 リカバリー戦略
- リトライポリシー
  ```python
  {
    "max_retries": 3,
    "initial_delay": 1,  # 秒
    "max_delay": 10,     # 秒
    "backoff_factor": 2
  }
  ```
- エラー通知
  - ログレベルに応じた通知設定
  - クリティカルエラー時の即時通知
  - エラー集計とレポート生成

## 5. 設定管理

### 5.1 環境変数

主な設定項目：
- APIキー
- 音声ファイル管理設定
- Redis接続設定
- エージェント固有の設定
  - LLM設定
  - TTS設定
  - 外部サービス連携設定

### 5.2 エージェント設定

各エージェントは以下の要素を設定可能：
- 基本情報（名前、システムプロンプト）
- LLMサービス設定
  - メッセージ生成用
  - 感情生成用
  - 画像認識用
- 音声設定
  - TTSタイプ
  - スピーカーモデル
  - スピーカーID
- サービス連携設定
  - LINEチャンネル情報等

## 6. 拡張性

### 6.1 新規エンドポイント追加

1. `/api/v1/`に新規エンドポイントファイルを作成
2. 必要なスキーマを`/schemas/`に定義
3. `main.py`にルーターを追加

### 6.2 新規サービス連携

1. 対応するサービスクライアントを実装
2. 必要な設定項目を`config.py`に追加
3. エージェント設定に統合

## 7. デプロイメント

### 7.1 必要要件

- Python 3.8以上
- Redis（オプション）
- 外部サービス
  - VoicevoxEngine（TTS用）
  - LLMサービス（OpenAI等）

### 7.2 デプロイメント方法

#### Docker Compose
```yaml
services:
  app:
    build: .
    ports:
      - "8080:8080"
    env_file:
      - .env
    volumes:
      - ./audio_files:/app/audio_files
```

#### 手動デプロイ
1. 依存パッケージのインストール
2. 環境変数の設定
3. uvicornでサーバー起動

## 8. セキュリティ

### 8.1 認証・認可

- APIキーによるアクセス制御
- 環境変数による機密情報管理

### 8.2 データ保護

- 一時ファイルの自動削除
- トークン使用量の制限
- CORSポリシーの設定

## 9. 今後の展開

### 9.1 開発予定機能

- ビデオ対応
- 新規プラットフォーム連携
  - Slack
  - Discord
- 新規TTSエンジン対応
  - OpenAI
  - Style-Bert-VITS2
- OpenAI Whisper対応

### 9.2 改善予定項目

- パフォーマンス最適化
- スケーラビリティ向上
- モニタリング機能強化
- テスト自動化

## 10. 運用管理

### 10.1 現在の運用機能

#### 10.1.1 ログ管理
- FastAPIの標準ログ機能を使用
  ```python
  logging.basicConfig(
      level=logging.INFO,
  )
  ```
- 主なログ出力
  - APIリクエスト・レスポンス
  - エラー情報
  - デバッグ情報（開発時）

#### 10.1.2 エラーハンドリング
- 例外処理による基本的なエラー制御
- FastAPIの標準エラーレスポンス
- Redis接続エラーのハンドリング

### 10.2 将来的な運用機能（計画中）

#### 10.2.1 拡張予定の監視機能
- 詳細なメトリクス収集
- パフォーマンスモニタリング
- アラート設定

#### 10.2.2 スケーラビリティ対応
- 複数インスタンス対応
- Redis設定の最適化
- キャッシュ戦略の実装

#### 10.2.3 バックアップ戦略
- 会話履歴のバックアップ
- 設定管理の改善
- 障害復旧手順の整備