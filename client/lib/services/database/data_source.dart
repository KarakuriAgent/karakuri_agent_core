import 'package:karakuri_agent/models/agent_config.dart';

abstract class DataSource {
  Future<int> insertAgentConfig(AgentConfig config);
  Future<bool> updateAgentConfig(AgentConfig config);
  Future<bool> deleteAgentConfig(int configId);
  Future<List<AgentConfig>> queryAllAgentConfig();
  Future<void> close();
}
