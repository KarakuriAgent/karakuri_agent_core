import 'dart:async';
import 'dart:convert';
import 'package:async/async.dart';

import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/agent_response.dart';
import 'package:http/http.dart' as http;
import 'package:karakuri_agent/services/agent/agent_service.dart';
import 'package:karakuri_agent/utils/log.dart';

class KarakuriAgentService extends AgentService {
  final AgentConfig _agentConfig;
  CancelableOperation<AgentResponse?>? _chatOperation;

  KarakuriAgentService(this._agentConfig);

  @override
  Future<AgentResponse?> sendMessage(String message) async {
    try {
      _chatOperation = CancelableOperation<AgentResponse?>.fromFuture(
        _chat(message),
      );
      await _chatOperation?.valueOrCancellation();
      if (_chatOperation == null || _chatOperation!.isCanceled) {
        return null;
      }
      return _chatOperation?.value;
    } finally {
      _chatOperation = null;
    }
  }

  @override
  Future<void> cancel() async {
    await _chatOperation?.cancel();
    _chatOperation = null;
  }

  @override
  Future<void> dispose() async {
    await cancel();
  }

  Future<AgentResponse?> _chat(String message) async {
    final uri = Uri.parse('${_agentConfig.baseUrl}/v1/chat/text/voice');

    final headers = {
      'X-API-Key': _agentConfig.apiKey,
      'accept': 'application/json',
      'Content-Type': 'application/json'
    };

    final body = {'agent_id': _agentConfig.agentId, 'message': message};

    try {
      final response = await http.post(uri,
          headers: headers,
          body: json.encode(body),
          encoding: Encoding.getByName('utf-8'));
      if (response.statusCode == 200 && response.bodyBytes.isNotEmpty) {
        final decodedBody = utf8.decode(response.bodyBytes);
        return AgentResponse.fromJson(json.decode(decodedBody));
      } else {
        final errorResponse = response.body;
        final errorMessage = json.decode(errorResponse)['error']['message'];
        debugPrint('HTTP ${response.statusCode}: $errorMessage');
        return null;
      }
    } catch (e, stackTrace) {
      debugPrint(stackTrace.toString());
      return null;
    }
  }
}
