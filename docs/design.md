# Karakuri Agent - Implementation Guide

## Project Overview
Karakuri Agent is an open-source AI agent platform that enables dialogue through various interfaces including chat tools, web applications, and smart speakers. A single agent can be accessed through multiple interfaces, and multiple agents can be configured with their own unique personalities, voices, and models.

## System Features

### Multimodal Dialogue
- Text-based dialogue
- Voice dialogue (TTS/STT)
- Dialogue with image recognition
- Combination of text, voice, and image

### Emotion Expression System
- Emotion analysis for agent responses
- Over 40 emotion categories
- Supports from system states (noticed, progress) to detailed emotion expressions

### Memory System
- Long-term memory management using Zep
  - Support for both self-hosted Zep and Zep Cloud
  - Persistent conversation history
  - User-specific context management
  - Conversation session management
  - Relevant facts extraction and utilization in system prompts
  - Redis caching for performance optimization
    - Session memory caching
    - Facts caching for cross-session context preservation
- User management functionality
  - Add and delete users
  - Retrieve user information
  - List all users

### Technology Stack
- FastAPI (Web Framework)
- Zep (Memory Management)
- Docker (Environment Setup)
- LiteLLM (LLM Integration)
- LINE Messaging API (LINE Bot Integration)

## Core Features

### Agent Configuration
- Custom system prompts
- Multiple LLM model settings (message generation, emotion generation, image recognition)
- Voice settings (VOICEVOX, NijiVoice, etc.)
- LINE bot integration settings

### Interfaces
1. RESTful API
   - Text/voice chat endpoints
   - Agent management
   - User management
   - Health check
   - OpenAI Chat API compatibility

2. WebSocket
   - Real-time bidirectional communication
   - Token-based authentication
   - Included WebSocket test page

3. LINE Bot
   - Text message support
   - Image message support
   - Voice reply functionality

## Security
- API key authentication
- Token-based WebSocket authentication
- Configurable CORS control
- Automatic voice file cleanup

## Extensibility
- Easy addition of new TTS providers
- Support for multiple LLM providers
- Flexible agent scaling
- Modularized design

## Configuration & Deployment
- Flexible configuration through environment variables
- Easy deployment with Docker Compose
  - Karakuri Agent Server
  - Zep Memory Server
  - Redis Cache
- Separation of development and production environments
- Redis persistence support

## License
- Free for non-commercial use (modification and redistribution allowed)
- Separate license required for commercial use
- Copyright notice and distribution conditions required

## Reference for Detailed Specifications
- API details: Files under `app/api/v1/`
- Schema definitions: Files under `app/schemas/`
- Core logic: Files under `app/core/`
- Configuration example: `example.env`
- License: `LICENSE` and `LICENSE_JP`

Using this platform, AI agents can maintain consistent personality and functionality while interacting with users through various interfaces.
