import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/services/database/local_datasource.dart';

class ConfigStorageRepository {
  final LocalDatasource _datasource;

  ConfigStorageRepository(this._datasource);

  Future<int> addServiceConfig(ServiceConfig config) async {
    return await _datasource.insertServiceConfig(config);
  }

  Future<bool> updateServiceConfig(ServiceConfig config) async {
    return await _datasource.updateServiceConfig(config);
  }

  Future<bool> deleteServiceConfig(int configId) async {
    return await _datasource.deleteServiceConfig(configId);
  }

  Future<List<ServiceConfig>> loadServiceConfigs() async {
    return await _datasource.queryAllServiceConfig();
  }

  Future<List<ServiceConfig>> loadTextServiceConfigs() async {
    return await _datasource.queryTextServiceConfig();
  }

  Future<List<ServiceConfig>> loadSpeechToTextServiceConfigs() async {
    return await _datasource.querySpeechToTextServiceConfig();
  }

  Future<List<ServiceConfig>> loadTextToSpeechServiceConfigs() async {
    return await _datasource.queryTextToSpeechServiceConfig();
  }

  Future<int> addAgentConfig(AgentConfig config) async {
    return await _datasource.insertAgentConfig(config);
  }

  Future<bool> updateAgentConfig(AgentConfig config) async {
    return await _datasource.updateAgentConfig(config);
  }

  Future<bool> deleteAgentConfig(int configId) async {
    return await _datasource.deleteAgentConfig(configId);
  }

  Future<List<AgentConfig>> loadAgentConfigs() async {
    return await _datasource.queryAllAgentConfig();
  }
}
