# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

import aiohttp
from fastapi import HTTPException
from typing import cast
from linebot import AsyncLineBotApi  # type: ignore
from linebot.aiohttp_async_http_client import AiohttpAsyncHttpClient  # type: ignore
from linebot.v3.messaging.async_api_client import AsyncApiClient  # type: ignore
from linebot.v3.messaging import AsyncMessagingApi  # type: ignore
from linebot.v3.webhook import WebhookParser  # type: ignore
from linebot.v3.webhooks.models import Event  # type: ignore
from linebot.v3.messaging.models import (  # type: ignore
    PushMessageRequest,
    ReplyMessageRequest,
    TextMessage,
    AudioMessage,
)
from linebot.v3.exceptions import (  # type: ignore
    InvalidSignatureError,
)
from linebot.v3.webhooks import (  # type: ignore
    MessageEvent,
    TextMessageContent,
    ImageMessageContent,
    Configuration,
    Source,
)
from app.core.chat.chat_client import ChatClient
from app.schemas.agent import AgentConfig
from app.schemas.chat_message import ChatMessage, MessageContent, MessageType
from app.core.date_util import DateUtil


class LineChatClient(ChatClient):
    line_messaging_api: AsyncMessagingApi
    line_bot_api: AsyncLineBotApi
    aio_session: aiohttp.ClientSession
    async_client: AsyncApiClient | None

    def create(self, agent_config: AgentConfig):
        self.aio_session = aiohttp.ClientSession()
        configuration = Configuration(
            access_token=agent_config.line_channel_access_token
        )
        self.async_client = AsyncApiClient(configuration)
        self.line_messaging_api = AsyncMessagingApi(self.async_client)

        aio_client = AiohttpAsyncHttpClient(self.aio_session)
        self.line_bot_api = AsyncLineBotApi(
            channel_access_token=agent_config.line_channel_access_token,
            async_http_client=aio_client,
        )

    def parse_line_events(
        self, body: str, signature: str, line_channel_secret: str
    ) -> list[Event]:
        line_parser = WebhookParser(line_channel_secret)

        try:
            events: list[Event] = cast(list[Event], line_parser.parse(body, signature))  # type: ignore
        except InvalidSignatureError:
            raise HTTPException(status_code=400, detail="Invalid signature")
        return events

    async def process_message(self, events: list[Event]) -> list[ChatMessage]:
        result: list[ChatMessage] = []
        for event in events:
            if not isinstance(event, MessageEvent):
                continue
            if isinstance(event.source, Source):
                id: str = ""
                if event.source.type == "user":
                    id = event.source.to_dict().get("userId") or ""
                elif event.source.type == "group":
                    id = event.source.to_dict().get("groupId") or ""
                elif event.source.type == "room":
                    id = event.source.to_dict().get("roomId") or ""
                else:
                    continue
            else:
                continue
            if id == "":
                continue
            token = event.reply_token
            if not isinstance(token, str):
                continue
            if isinstance(event.message, ImageMessageContent):
                image = await self._process_image_message(event)
                content = MessageContent(
                    type=MessageType.IMAGE,
                    image=image,
                )
            elif isinstance(event.message, TextMessageContent):
                content = MessageContent(type=MessageType.TEXT, text=event.message.text)
            else:
                continue

            message = ChatMessage(
                reply_token=token,
                content=content,
                id=id,
                timestamp=DateUtil.now(),
            )
            result.append(message)

        return result

    async def _process_image_message(self, event: MessageEvent) -> bytes:
        message_content = await self.line_bot_api.get_message_content(event.message.id)  # type: ignore
        image_bytes: bytes = b""
        async for chunk in message_content.iter_content():  # type: ignore
            assert isinstance(chunk, bytes)
            image_bytes += chunk
        return image_bytes  # type: ignore

    async def reply_message(
        self, token: str, message: str, audio_url: str, duration: int
    ):
        await self.line_messaging_api.reply_message(  # type: ignore
            ReplyMessageRequest(
                reply_token=token,  # type: ignore
                messages=[
                    TextMessage(text=message),  # type: ignore
                    AudioMessage(
                        original_content_url=audio_url,  # type: ignore
                        duration=duration,
                    ),
                ],
            )
        )

    async def push_message(self, id: str, message: str, audio_url: str, duration: int):
        await self.line_messaging_api.push_message(  # type: ignore
            PushMessageRequest(
                to=id,
                messages=[
                    TextMessage(text=message),  # type: ignore
                    AudioMessage(
                        original_content_url=audio_url,  # type: ignore
                        duration=duration,
                    ),
                ],
            )
        )

    async def close(self):
        await self.aio_session.close()
        if self.async_client is not None:
            await self.async_client.close()
