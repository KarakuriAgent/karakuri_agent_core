import 'dart:async';

import 'package:karakuri_agent/models/agent_response.dart';
import 'package:karakuri_agent/services/agent/agent_service.dart';

class AgentRepository {
  late final AgentService _service;

  AgentRepository(this._service);

  Future<AgentResponse?> sendMessage(String message) async {
    return await _service.sendMessage(message);
  }

  Future<void> cancel() async {
    await _service.cancel();
  }

  Future<void> dispose() async {
    await _service.dispose();
  }
}
