# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
import base64
import io
import json
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.websockets import WebSocket
from jsonschema import ValidationError
from app.core.agent_manager import get_agent_manager
from app.core.config import get_settings
from app.dependencies import get_llm_service, get_stt_service, get_tts_service
from app.schemas.web_socket import AudioRequest, AudioResponse, ImageAudioRequest, ImageTextRequest, TextRequest, TextResponse
from app.utils.audio import calculate_audio_duration, upload_to_storage
from app.core.llm_service import LLMService
from app.core.stt_service import STTService
from app.core.tts_service import TTSService

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)
UPLOAD_DIR = settings.web_socket_audio_files_dir
MAX_FILES = settings.web_socket_max_audio_files

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket,
    llm_service: LLMService = Depends(get_llm_service),
    stt_service: STTService = Depends(get_stt_service),
    tts_service: TTSService = Depends(get_tts_service)):
    await websocket.accept()
    agent_manager = get_agent_manager()
    while True:
        try:
            message = await websocket.receive_text()
            raw_data = json.loads(message)
            msg_type = raw_data.get("request_type")
            request_obj = None
            if msg_type == "text":
                request_obj = TextRequest(**raw_data)
            elif msg_type == "audio":
                request_obj = AudioRequest(**raw_data)
            elif msg_type == "image_text":
                request_obj = ImageTextRequest(**raw_data)
            elif msg_type == "image_audio":
                request_obj = ImageAudioRequest(**raw_data)
            else:
                await websocket.send_text(json.dumps({"type": "text", "text": "unknown request type"}))
                continue

            agent_config = agent_manager.get_agent(request_obj.agent_id)
            image_content: Optional[bytes] = None
            text_message: str = ""

            if isinstance(request_obj, AudioRequest):
                audio_bytes = base64.b64decode(request_obj.audio)
                audio_file = io.BytesIO(audio_bytes)
                audio_content = audio_file.read() 
                text_message = await stt_service.transcribe_audio(
                    audio_content,
                    agent_config
                 )
            elif isinstance(request_obj, ImageAudioRequest):
                audio_bytes = base64.b64decode(request_obj.audio)
                audio_file = io.BytesIO(audio_bytes)
                audio_content = audio_file.read() 
                text_message = await stt_service.transcribe_audio(
                    audio_content,
                    agent_config
                 )
                image_bytes = base64.b64decode(request_obj.image)
                image_file = io.BytesIO(image_bytes)
                image_content = image_file.read() 
            elif isinstance(request_obj, ImageTextRequest):
                text_message = request_obj.text
                image_bytes = base64.b64decode(request_obj.image)
                image_file = io.BytesIO(image_bytes)
                image_content = image_file.read() 
            else:
                text_message = request_obj.text
            llm_response = await llm_service.generate_response(
                "websocket",
                text_message, 
                agent_config,
                image=image_content
            )

            agent_message = llm_response.agent_message.rstrip('\n')
            emotion = llm_response.emotion

            if request_obj.responce_type == "text":
                response = TextResponse(user_message=text_message, agent_message=agent_message, emotion=emotion)
            elif request_obj.responce_type == "audio":
                audio_data = await tts_service.generate_speech(
                    agent_message, 
                    agent_config
                )

                scheme = websocket.headers.get('X-Forwarded-Proto', 'http')
                server_host = websocket.headers.get('X-Forwarded-Host', websocket.base_url.hostname)
                base_url = f"{scheme}://{server_host}"
        
                audio_url = await upload_to_storage(base_url, audio_data, "ws", UPLOAD_DIR, MAX_FILES)
                duration = calculate_audio_duration(audio_data)
                response = AudioResponse(user_message=text_message,
                                         agent_message=agent_message,
                                         emotion=emotion,
                                         audio_url=audio_url, 
                                         duration=duration
                )
            else:
                await websocket.send_text(json.dumps({"type": "text", "text": "unknown response type"}))
                continue

            await websocket.send_text(response.model_dump_json())
        except ValidationError as e:
            error_msg = f"Invalid message format: {e}"
            await websocket.send_text(json.dumps({"type": "text", "text": error_msg}))
        except Exception as e:
            error_msg = f"Exception format: {e}"
            await websocket.send_text(json.dumps({"type": "text", "text": error_msg}))
            await websocket.close()
            break


@router.get(f"/{UPLOAD_DIR}/{{file_name}}")
async def get_audio(file_name: str):
    if '..' in file_name or '/' in file_name:
        raise HTTPException(status_code=400, detail="Invalid file name")
    file_path = Path(f"{UPLOAD_DIR}/{file_name}.wav")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path)


@router.get("/ws-test", response_class=HTMLResponse)
def ws_test_page():
    initial_message = json.dumps({
        "request_type": "text",
        "responce_type": "text",
        "agent_id": "1",
        "text": "こんにちは"
    }, ensure_ascii=False, indent=2)
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>WebSocket Test</title></head>
    <body>
        <h1>WebSocket Test Page</h1>
        <div>
            <p>以下のテキストエリアにJSONメッセージを入力し、"Send"ボタンで送信してください。</p>
            <p>画像を添付したい場合はファイルを選択してください。選択時に request_type が自動で "image_text" に変わります。</p>
            <textarea id="msgInput" rows="10" cols="60">{initial_message}</textarea><br>
            <input type="file" id="fileInput" accept="image/*"/><br><br>
            <button id="sendBtn">Send</button>
        </div>
        <pre id="log"></pre>

        <script>
            const logArea = document.getElementById('log');
            const protocol = (window.location.protocol === 'https:') ? 'wss:' : 'ws:';
            const ws = new WebSocket(protocol + '//' + window.location.host + '/v1/ws');

            // 画像ファイルの base64 データを保持するための変数
            let imageBase64 = null;

            // WebSocket イベント
            ws.onopen = () => {{
                logArea.textContent += "WebSocket connection opened\\n";
            }};

            ws.onmessage = (event) => {{
                logArea.textContent += "Received: " + event.data + "\\n";
            }};

            ws.onclose = () => {{
                logArea.textContent += "WebSocket connection closed\\n";
            }};

            // 画像ファイルが選択されたときの処理
            document.getElementById('fileInput').onchange = (event) => {{
                const file = event.target.files[0];
                if (!file) {{
                    // ファイルがクリアされた場合は初期化
                    imageBase64 = null;
                    return;
                }}

                // FileReader で画像を base64 に変換
                const reader = new FileReader();
                reader.onload = () => {{
                    imageBase64 = reader.result.split(",")[1]; // "data:xxx;base64,～～" の後ろだけを切り出し

                    // JSON テキストエリアを読み込み
                    let msgObj;
                    try {{
                        msgObj = JSON.parse(document.getElementById('msgInput').value);
                    }} catch (e) {{
                        logArea.textContent += "JSON Parse Error: " + e + "\\n";
                        return;
                    }}

                    // imageBase64 があるので request_type を "image_text" に変更し、
                    // image フィールドを追加。テキスト欄は任意で使ってください
                    msgObj.request_type = "image_text";
                    msgObj.image = imageBase64;

                    // JSON テキストエリアの表示も更新
                    document.getElementById('msgInput').value = JSON.stringify(msgObj, null, 2);
                }};
                reader.readAsDataURL(file);
            }};

            // Send ボタンが押されたときに送信
            document.getElementById('sendBtn').onclick = () => {{
                const msg = document.getElementById('msgInput').value;
                ws.send(msg);
                logArea.textContent += "Sent: " + msg + "\\n";
            }};
        </script>
    </body>
    </html>
    """
