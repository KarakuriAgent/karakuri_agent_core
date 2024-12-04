import 'dart:async';

import 'package:karakuri_agent/models/agent_responce.dart';
import 'package:karakuri_agent/services/agent/agent_service.dart';

class AgentRepository {
  late final AgentService _service;

  AgentRepository(this._service);

  Future<AgentResponce?> sendMessage(String message) async {
    return await _service.sendMessage(message);
  }

  void cancel() {
    _service.cancel();
  }

  Future<void> dispose() async {
    _service.dispose();
  }
}
