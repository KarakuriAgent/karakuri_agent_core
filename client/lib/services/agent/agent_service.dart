import 'package:karakuri_agent/models/agent_response.dart';

abstract class AgentService {
  Future<AgentResponse?> sendMessage(String message);
  void cancel();
  void dispose();
}
