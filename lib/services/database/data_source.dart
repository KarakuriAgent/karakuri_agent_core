import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/service_config.dart';

abstract class DataSource {
  Future<int> insertServiceConfig(ServiceConfig serviceConfig);
  Future<bool> updateServiceConfig(ServiceConfig serviceConfig);
  Future<bool> deleteServiceConfig(int configId);
  Future<List<ServiceConfig>> queryAllServiceConfig();
  Future<List<ServiceConfig>> queryTextServiceConfig();
  Future<List<ServiceConfig>> querySpeechToTextServiceConfig();
  Future<List<ServiceConfig>> queryTextToSpeechServiceConfig();
  Future<int> insertAgentConfig(AgentConfig config);
  Future<bool> updateAgentConfig(AgentConfig config);
  Future<bool> deleteAgentConfig(AgentConfig config);
  Future<List<AgentConfig>> queryAllAgentConfig();
  Future<void> close();
}
