import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/services/text_to_speech/openai_text_to_speech_service.dart';
import 'package:karakuri_agent/services/text_to_speech/sbv2_text_to_speech_service.dart';
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
      case ServiceType.styleBertVITS2:
        _service = Sbv2TextToSpeechService(_agentConfig);
      default:
        throw Exception(
            'Unsupported Text-to-Speech service type: ${_agentConfig.textServiceConfig.type}');
    }
  }

  Future<void> dispose() async {
    _service.dispose();
  }

  Future<void> speech(String text) async {
    await _service.speech(text);
  }

  Future<void> stop() async {
    _service.stop();
  }
}
