import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/services/database/data_source.dart';
import 'package:karakuri_agent/services/database/sqflite_helper.dart';

class LocalDatasource implements DataSource {
  final SqfliteHelper _databaseHelper = SqfliteHelper.instance;

  @override
  Future<int> insertServiceConfig(ServiceConfig serviceConfig) async {
    return await _databaseHelper.insertServiceConfig(serviceConfig);
  }

  @override
  Future<bool> updateServiceConfig(ServiceConfig serviceConfig) async {
    return await _databaseHelper.updateServiceConfig(serviceConfig);
  }

  @override
  Future<bool> deleteServiceConfig(int configId) async {
    return await _databaseHelper.deleteServiceConfig(configId);
  }

  @override
  Future<List<ServiceConfig>> queryAllServiceConfig() async {
    return await _databaseHelper.queryAllServiceConfig();
  }

  @override
  Future<List<ServiceConfig>> queryTextServiceConfig() async {
    return await _databaseHelper.queryTextServiceConfig();
  }

  @override
  Future<List<ServiceConfig>> querySpeechToTextServiceConfig() async {
    return await _databaseHelper.querySpeechToTextServiceConfig();
  }

  @override
  Future<List<ServiceConfig>> queryTextToSpeechServiceConfig() async {
    return await _databaseHelper.queryTextToSpeechServiceConfig();
  }

  @override
  Future<int> insertAgentConfig(AgentConfig config) async {
    return await _databaseHelper.insertAgentConfig(config);
  }

  @override
  Future<bool> updateAgentConfig(AgentConfig config) async {
    return await _databaseHelper.updateAgentConfig(config);
  }

  @override
  Future<bool> deleteAgentConfig(int configId) async {
    return await _databaseHelper.deleteAgentConfig(configId);
  }

  @override
  Future<List<AgentConfig>> queryAllAgentConfig() async {
    return await _databaseHelper.queryAllAgentConfig();
  }

  @override
  Future<void> close() async => await _databaseHelper.close();
}
