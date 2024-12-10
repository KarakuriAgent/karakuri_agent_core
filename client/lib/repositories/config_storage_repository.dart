// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/services/database/data_source.dart';

class ConfigStorageRepository {
  final DataSource _datasource;

  ConfigStorageRepository(this._datasource);

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
