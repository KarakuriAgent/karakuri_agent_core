# 🤖 Karakuri Agent

日本語版はこちら [README_JP.md](README_JP.md).

**Karakuri Agent** is an open-source project aiming to create an **AI agent** accessible from any environment—whether it's a smart speaker, chat tool, or web application. By integrating various endpoints and services, it aims to realize a world where you can **access a single agent** from **anywhere**.  
You can also define multiple agents simultaneously, each with unique roles, personalities, voices, and models.

## Project Structure

```
.
├─ server/
│  ├─ app/
│  ├─ requirements.txt
│  ├─ example.env
│  └─ ...
├─ client/
│  ├─ lib/
│  ├─ pubspec.yaml
│  └─ ...
└─ compose.yml
```

## Technical Overview

### 🚀 **Server-Side**
- Framework: FastAPI

### 📱 **Client-Side**
- Framework: Flutter

| Platform | Support Status       |
|----------|----------------------|
| Android  | 🟢 Supported         |
| iOS      | 🟢 Supported         |
| Web      | 🟢 Supported         |
| Mac      | 🟢 Supported         |
| Windows  | ❌ Not supported yet (planned) |
| Linux    | ❌ Not supported yet (planned) |

### 🪶 **Model Support (LLM)**
By utilizing LiteLLM, you can access models supported by [LiteLLM](https://github.com/BerriAI/litellm), such as OpenAI and Ollama.  
- **Example for OpenAI models**: Obtain an [OpenAI API Key](https://platform.openai.com/) and configure it in `.env`.  
- **Example for Ollama models**: Run [Ollama](https://docs.ollama.ai/) locally and set its URL in `.env`.

### 🎙️ **Text-To-Speech (TTS)**

| Service            | Support Status        |
|--------------------|-----------------------|
| Voicevox Engine     | 🟢 Supported          |
| AivisSpeech Engine  | 🟢 Supported          |
| Style-Bert-VITS2    | ❌ Not supported yet (planned) |

**Example for VoicevoxEngine Setup**:  
VoicevoxEngine must be running locally.  
Follow the [official documentation](https://github.com/VOICEVOX/voicevox_engine) to start it.  
Then set the endpoint (e.g., `http://localhost:50021`) in `AGENT_1_TTS_BASE_URL` within your `.env` file.

### 🎧 **Speech-To-Text (STT)**

| Service         | Support Status        |
|-----------------|-----------------------|
| faster-whisper  | 🟢 Supported          |
| OpenAI Whisper  | ❌ Not supported yet (planned) |

`faster-whisper` works as a Python library and does not require an external service.  
Once installed via `requirements.txt`, it's ready to use.

### **Endpoints**

| Endpoint        | Support Status             |
|-----------------|----------------------------|
| text to text    | 🟢 Supported               |
| text to voice   | 🟢 Supported               |
| text to video   | ❌ Not supported yet (planned) |
| voice to text   | 🟢 Supported               |
| voice to voice  | 🟢 Supported               |
| voice to video  | ❌ Not supported yet (planned) |
| video to text   | ❌ Not supported yet (planned) |
| video to voice  | ❌ Not supported yet (planned) |
| video to video  | ❌ Not supported yet (planned) |

### **Service Integrations**

| Service  | Support Status             |
|----------|----------------------------|
| LINE     | 🟢 Supported               |
| Slack    | ❌ Not supported yet (planned) |
| Discord  | ❌ Not supported yet (planned) |

For unsupported features or services, please check the [Project tab](https://github.com/0235-jp/karakuri_agent/projects) or [Discussions](https://github.com/0235-jp/karakuri_agent/discussions) for updates and roadmap.

## ⚡ Features

- **Wide Range of Endpoints**  
  - 📝 Text to Text  
  - 💬 Text to Voice  
  - 🎤 Voice to Text 
  - 🔄 Voice to Voice

- **Flexible Model Selection**  
  By using LiteLLM, you can support any models that LiteLLM supports (e.g., OpenAI, Ollama).

- **Multiple Agent Management**  
  You can define multiple agents in `.env`, customizing roles, personalities, voice profiles, and more.

- **Service Integration**  
  Currently integrates with **LINE**. Future plans include other messaging services and voice interfaces.

## 🎥 Demo / Screenshots

*Under development—will be added later!*  
We plan to provide screenshots or GIFs showing the Flutter client and voice interaction.

## 📦 Requirements

- **Server-Side**  
  - Python 3.8 or later  
  - (Optional) VoicevoxEngine for TTS  
    - Run VoicevoxEngine locally and set the URL in `.env`.  
  - (Optional) For LINE integration, obtain tokens and a secret from the [LINE Developer Console](https://developers.line.biz/en/).

- **Client (Flutter)**  
  - Flutter SDK (latest recommended)  
  *Supports Android/iOS/Web/Mac; Windows/Linux support is planned.*

- **LLM Model Usage**  
  - Requires valid API keys and an internet connection.

- **Ollama Model Usage**  
  - Requires Ollama running locally.

## 🛠️ Installation

### Using Docker Compose

If you have `compose.yml` at the project root, you can start both the server and the web client with Docker Compose.

```bash
docker compose up
```

After running this command:  
- Server will be available at `http://localhost:8080`  
- Web client will be available at `http://localhost:5050`

Make sure to set up `.env` in the `server` directory beforehand.

### Manual Setup: Server-Side

1. Move to the server directory:  
   ```bash
   cd server
   ```
2. Copy and edit `.env` as needed:  
   ```bash
   cp example.env .env
   ```
   Configure agents, models, API keys, etc. in `.env`.
   
3. Install required packages:  
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:  
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
   ```
   → Server will run at `http://localhost:8080`.

### Manual Setup: Client (Flutter)

1. Move to the client directory:  
   ```bash
   cd client
   ```
2. Resolve dependencies:  
   ```bash
   flutter pub get
   ```
3. Run the application (example for Web; see `pubspec.yaml` scripts for details):  
   ```bash
   dart run rps run-release web
   ```
   → Web client will run at `http://localhost:5050`.

## 💡 Usage

- Check and interact with the API format via Swagger UI:  
  `http://localhost:8080/docs`

- Access the Flutter web app at `http://localhost:5050` and input the API server information to interact with the AI agent.

## ⚙️ Configuration

You can configure the application via `.env` or environment variables. Example:  
```
API_KEYS=Specify server access API keys separated by commas
LINE_MAX_AUDIO_FILES=Max number of audio files for LINE integration (e.g., 5)
LINE_AUDIO_FILES_DIR=line_audio_files
CHAT_MAX_AUDIO_FILES=Max number of audio files for Chat endpoint (e.g., 5)
CHAT_AUDIO_FILES_DIR=chat_audio_files

AGENT_1_NAME=Name of the agent
AGENT_1_MESSAGE_GENERATE_LLM_BASE_URL=Base URL for message generation LLM (LiteLLM style)
AGENT_1_MESSAGE_GENERATE_LLM_API_KEY=API key for message generation LLM
AGENT_1_MESSAGE_GENERATE_LLM_MODEL=Model for message generation LLM (LiteLLM style)
AGENT_1_EMOTION_GENERATE_LLM_BASE_URL=Base URL for emotion generation LLM (LiteLLM style)
AGENT_1_EMOTION_GENERATE_LLM_API_KEY=API key for emotion generation LLM
AGENT_1_EMOTION_GENERATE_LLM_MODEL=Model for emotion generation LLM (LiteLLM style)
AGENT_1_TTS_TYPE=TTS type (supported: voicevox; use voicevox for AivisSpeech as well)
AGENT_1_TTS_BASE_URL=TTS endpoint URL
AGENT_1_TTS_API_KEY=TTS API key (can be blank)
AGENT_1_TTS_SPEAKER_MODEL=TTS model (e.g., default)
AGENT_1_TTS_SPEAKER_ID=TTS speaker ID
AGENT_1_LLM_SYSTEM_PROMPT=System prompt for the agent
AGENT_1_LINE_CHANNEL_SECRET=LINE channel secret (required if LINE integration is used)
AGENT_1_LINE_CHANNEL_ACCESS_TOKEN=LINE channel access token (required if LINE integration is used)

# Increase AGENT_2_, AGENT_3_, etc. for multiple agents
```

## 🤝 Contributing

1. Feel free to file issues for bugs or improvement suggestions!  
2. Create a working branch from `main` and open a Pull Request.  
3. Feature proposals and questions are also welcome in [Discussions](https://github.com/0235-jp/karakuri_agent/discussions).

## 📜 About the License

This project is provided under a custom license agreement.

- **Non-Commercial Use**: Non-commercial use, such as personal learning, research, or hobby projects, is permitted free of charge. If you redistribute modified versions, please retain the original copyright notice and the full text of the license.
  
- **Commercial Use**: If you wish to use this software or its derivatives for commercial purposes or to generate revenue, you must obtain a commercial license from 0235 Inc. in advance.  
  If you have any questions or need to acquire a commercial license, please contact us at [karakuri-agent-support@0235.co.jp](mailto:karakuri-agent-support@0235.co.jp).

For more details, please see the [LICENSE](LICENSE) file.

## 🛠️ Support for setup, configuration, and ongoing operation

We also offer paid support for setup, configuration, and ongoing operation. Fees depend on your requirements. For more information, please contact us at [karakuri-agent-support@0235.co.jp](mailto:karakuri-agent-support@0235.co.jp)

## 🔗 Related Projects / References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)  
- [Flutter Documentation](https://docs.flutter.dev/)  
- [LINE Messaging API](https://developers.line.biz/en/docs/messaging-api/)  
- [LiteLLM](https://github.com/BerriAI/litellm)  
- [Voicevox Engine](https://github.com/VOICEVOX/voicevox_engine)  
- [AivisSpeech Engine](https://github.com/Aivis-Project/AivisSpeech-Engine)  
- [Style-Bert-VITS2](https://github.com/litagin02/Style-Bert-VITS2)  
- [faster-whisper](https://github.com/guillaumekln/faster-whisper)  
- [OpenAI Whisper](https://github.com/openai/whisper)  
- [Ollama](https://docs.ollama.ai/)
