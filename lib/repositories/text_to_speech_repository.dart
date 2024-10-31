import 'dart:typed_data';

import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/services/text_to_speech/openai_text_to_speech_service.dart';
import 'package:karakuri_agent/services/text_to_speech/text_to_speech_service.dart';
import 'package:karakuri_agent/services/text_to_speech/voicevox_text_to_speech_service.dart';

class TextToSpeechRepository {
  final AgentConfig _agentConfig;
  late final TextToSpeechService _service;

  TextToSpeechRepository(this._agentConfig) {
    switch (_agentConfig.textToSpeechServiceConfig.type) {
      case ServiceType.openAI:
        _service = OpenaiTextToSpeechService(_agentConfig);
        break;
      case ServiceType.voicevox:
      case ServiceType.voicevoxNemo:
        _service = VoicevoxTextToSpeechService(_agentConfig);
        break;
      default:
        throw Exception(
            'Unsupported Text-to-Speech service type: ${_agentConfig.textServiceConfig.type}');
    }
  }

  Future<Uint8List> synthesize(String text) async {
    return await _service.synthesize(text);
  }

  Future<void> play(Uint8List audioData) async {
    await _service.play(audioData);
  }

  Future<void> stop() async {
    _service.stop();
  }

  Future<void> dispose() async {
    _service.dispose();
  }
}
