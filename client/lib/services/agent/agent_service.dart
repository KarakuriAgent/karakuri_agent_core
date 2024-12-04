import 'package:karakuri_agent/models/agent_responce.dart';

abstract class AgentService {
  Future<AgentResponce?> sendMessage(String message);
  void cancel();
  void dispose();
}
