import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/models/text_message.dart';
import 'package:karakuri_agent/models/text_result.dart';
import 'package:karakuri_agent/services/text/openai_text_service.dart';
import 'package:karakuri_agent/services/text/text_service.dart';

class TextRepository {
  final AgentConfig _agentConfig;
  late final TextService _service;

  TextRepository(this._agentConfig) {
    switch (_agentConfig.textServiceConfig.type) {
      case ServiceType.openAI:
        _service = OpenaiTextService(_agentConfig);
        break;
      default:
        throw Exception(
            'Unsupported Text service type: ${_agentConfig.textServiceConfig.type}');
    }
  }

  Stream<TextResult> completionsStream(List<TextMessage> messages) {
    return _service.completionsStream(messages);
  }

  void cancel() {
    _service.cancel();
  }

  void dispose() {
    _service.dispose();
  }
}
