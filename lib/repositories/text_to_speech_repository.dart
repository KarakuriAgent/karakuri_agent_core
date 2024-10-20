import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/services/text_to_speech/openai_text_to_speech_service.dart';
import 'package:karakuri_agent/services/text_to_speech/text_to_speech_service.dart';

class TextToSpeechRepository {
  final AgentConfig _agentConfig;
  late final TextToSpeechService _service;

  TextToSpeechRepository(this._agentConfig) {
    switch (_agentConfig.textServiceConfig.type) {
      case ServiceType.openAI:
        _service = OpenaiTextToSpeechService(_agentConfig);
        break;
      default:
        throw Exception('Unsupported Text-to-Speech service type: ${_agentConfig.textServiceConfig.type}');
    }
  }

  Future<void> speech(String text) async {
    await _service.speech(text);
  }
}
