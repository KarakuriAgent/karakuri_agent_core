// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:karakuri_agent/models/agent_response.dart';
import 'package:karakuri_agent/services/agent/agent_service.dart';

class AgentRepository {
  final AgentService _service;

  AgentRepository(this._service);

  Future<AgentResponse?> sendMessage(String message) async {
     try {
     return await _service.sendMessage(message);
   } catch (e) {
     debugPrint('send message error: $e');
     return null;
   }
  }

  Future<void> cancel() async {
    await _service.cancel();
  }

  Future<void> dispose() async {
    await _service.dispose();
  }
}
