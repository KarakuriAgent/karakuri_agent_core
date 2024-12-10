import 'package:karakuri_agent/models/agent_response.dart';

abstract class AgentService {
  Future<AgentResponse?> sendMessage(String message);
  Future<void> cancel();
  Future<void> dispose();
}
