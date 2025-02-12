# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

from typing import Optional, cast, Tuple
from fastapi import HTTPException, Request, UploadFile

from app.core.config import Settings
from app.core.llm_service import LLMService
from app.core.tts_service import TTSService
from app.core.stt_service import STTService
from app.core.memory.memory_service import MemoryService
from app.core.agent_manager import AgentConfig, AgentManager
from app.schemas.user import UserConfig
from app.schemas.llm import LLMResponse
from app.schemas.talk import TextTalkResponse, VoiceTalkResponse
from app.utils.audio import calculate_audio_duration, get_base_url, upload_to_storage


class TalkFacade:
    """A service that encapsulates common operations for text and voice interactions.

    This class provides methods in the following hierarchy:

    1. High-level API (for external use)
        - handle_agent_response: The main entry point for all interaction processing.
          Automatically handles input type (text/voice) detection and output type switching.

    2. Mid-level API (for internal use)
        - process_text_message: Text input processing
        - process_voice_message: Voice input processing
        - generate_voice_response: Voice output generation

    It is recommended to use handle_agent_response in most cases.
    Individual methods should only be used when you need to:
    - Execute specific processing only
    - Implement custom error handling
    """

    def __init__(
        self,
        llm_service: LLMService,
        tts_service: TTSService,
        stt_service: STTService,
        memory_service: MemoryService,
        agent_manager: AgentManager,
        settings: Settings,
    ):
        """Initialize TalkFacade.

        Args:
            llm_service: Service for language model interactions
            tts_service: Service for text-to-speech conversion
            stt_service: Service for speech-to-text conversion
            memory_service: Service for memory management
            agent_manager: Service for agent management
            upload_dir: Directory for storing audio files
            max_files: Maximum number of audio files to keep
        """
        self._llm_service = llm_service
        self._tts_service = tts_service
        self._stt_service = stt_service
        self._memory_service = memory_service
        self._agent_manager = agent_manager
        self._upload_dir = settings.talk_audio_files_dir
        self._max_files = settings.talk_max_audio_files

    async def _get_configs(
        self, agent_id: str, user_id: str
    ) -> Tuple[AgentConfig, UserConfig]:
        """Get and validate agent and user configurations.

        Args:
            agent_id: Agent ID
            user_id: User ID

        Returns:
            Tuple of agent configuration and user configuration

        Raises:
            HTTPException: If agent or user is not found
        """
        try:
            agent_config = self._agent_manager.get_agent(agent_id)
        except KeyError:
            raise HTTPException(
                status_code=404, detail=f"Agent with ID '{agent_id}' not found."
            )

        user_config = await self._memory_service.get_user(agent_id, user_id)
        if user_config is None:
            raise HTTPException(
                status_code=404, detail=f"User with user_id '{user_id}' not found."
            )

        return agent_config, user_config

    async def _read_image_content(
        self, image_file: Optional[UploadFile]
    ) -> Optional[bytes]:
        """Read image content from file if present.

        Args:
            image_file: Optional image file

        Returns:
            Image content as bytes or None
        """
        if image_file is not None:
            return await image_file.read()
        return None

    async def process_text_message(
        self,
        message: str,
        agent_config: AgentConfig,
        user_config: UserConfig,
        image_content: Optional[bytes] = None,
    ) -> TextTalkResponse:
        """Process a text message and return a text response.

        This is an internal API. Use handle_agent_response in most cases.
        Only use this method directly when you need to:
        - Execute text input processing only
        - Implement custom error handling
        - Optimize performance

        Args:
            message: User's text message
            agent_config: Agent configuration
            user_config: User configuration
            image_content: Optional image data

        Returns:
            TextTalkResponse: Agent's text response
        """
        llm_response = cast(
            LLMResponse,
            await self._llm_service.generate_response(
                message_type="talk",
                message=message,
                agent_config=agent_config,
                user_config=user_config,
                image=image_content,
            ),
        )

        return TextTalkResponse(
            user_message=llm_response.user_message,
            agent_message=llm_response.agent_message,
            emotion=llm_response.emotion,
        )

    async def process_voice_message(
        self,
        audio_content: bytes,
        agent_config: AgentConfig,
        user_config: UserConfig,
        image_content: Optional[bytes] = None,
    ) -> TextTalkResponse:
        """Process a voice message and return a text response.

        This is an internal API. Use handle_agent_response in most cases.
        Only use this method directly when you need to:
        - Execute voice input processing only
        - Implement custom error handling
        - Optimize performance

        Args:
            audio_content: User's voice data
            agent_config: Agent configuration
            user_config: User configuration
            image_content: Optional image data

        Returns:
            TextTalkResponse: Agent's text response
        """
        text_message = await self._stt_service.transcribe_audio(audio_content)

        llm_response = cast(
            LLMResponse,
            await self._llm_service.generate_response(
                message_type="talk",
                message=text_message,
                agent_config=agent_config,
                user_config=user_config,
                image=image_content,
            ),
        )

        return TextTalkResponse(
            user_message=llm_response.user_message,
            agent_message=llm_response.agent_message,
            emotion=llm_response.emotion,
        )

    async def generate_voice_response(
        self,
        text_response: TextTalkResponse,
        agent_config: AgentConfig,
        base_url: str,
    ) -> VoiceTalkResponse:
        """Generate a voice response from a text response.

        This is an internal API. Use handle_agent_response in most cases.
        Only use this method directly when you need to:
        - Execute voice output generation only
        - Implement custom error handling
        - Optimize performance

        Args:
            text_response: Text response to convert
            agent_config: Agent configuration
            base_url: Base URL for audio files

        Returns:
            VoiceTalkResponse: Agent's voice response
        """
        audio_data = await self._tts_service.generate_speech(
            text_response.agent_message, agent_config
        )

        audio_url = await upload_to_storage(
            base_url, audio_data, "talk", self._upload_dir, self._max_files
        )

        duration = calculate_audio_duration(audio_data)

        return VoiceTalkResponse(
            user_message=text_response.user_message,
            agent_message=text_response.agent_message,
            emotion=text_response.emotion,
            audio_url=audio_url,
            duration=duration,
        )

    async def handle_agent_response(
        self,
        request: Request,
        agent_id: str,
        user_id: str,
        message: str | bytes,
        image_file: Optional[UploadFile] = None,
        generate_voice: bool = False,
    ) -> TextTalkResponse | VoiceTalkResponse:
        """Process an agent's response.

        This is the main entry point of TalkFacade.
        Use this method in most cases.

        This method provides:
        1. Automatic input type (text/voice) detection
        2. Appropriate message processing (text/voice)
        3. Output type (text/voice) switching
        4. Unified error handling
        5. Agent and user configuration validation
        6. Image file handling

        Args:
            request: FastAPI request object
            agent_id: Agent ID
            user_id: User ID
            message: Text message or voice data
            image_file: Optional image file
            generate_voice: Whether to generate a voice response

        Returns:
            Text response or voice response

        Raises:
            HTTPException: If there is an error processing the request
        """
        try:
            # Get agent and user configurations
            agent_config, user_config = await self._get_configs(agent_id, user_id)

            # Read image content if present
            image_content = await self._read_image_content(image_file)

            # Process message based on its type
            if isinstance(message, str):
                text_response = await self.process_text_message(
                    message, agent_config, user_config, image_content
                )
            else:
                text_response = await self.process_voice_message(
                    message, agent_config, user_config, image_content
                )

            # Generate voice response if requested
            if generate_voice:
                base_url = get_base_url(request)
                return await self.generate_voice_response(
                    text_response, agent_config, base_url
                )

            return text_response

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error processing request: {str(e)}"
            )
