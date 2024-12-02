import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/models/text_message.dart';
import 'package:karakuri_agent/services/text/karakuri_service.dart';

class TextRepository {
  final AgentConfig _agentConfig;
  late final KarakuriService _service;

  TextRepository(this._agentConfig) {
    switch (_agentConfig.textServiceConfig.type) {
      case ServiceType.openAI:
        _service = KarakuriService(_agentConfig);
        break;
      default:
        throw Exception(
            'Unsupported Text service type: ${_agentConfig.textServiceConfig.type}');
    }
  }

  Future<void> chat(String message) async {
    return await _service.chat(message);
  }

  Future<void> dispose() async {
    _service.dispose();
  }

  Future<void> stop() async {
    _service.stop();
  }
}
