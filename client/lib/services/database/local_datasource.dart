// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/services/database/data_source.dart';
import 'package:karakuri_agent/services/database/sqflite_helper.dart';

class LocalDatasource implements DataSource {
  final SqfliteHelper _databaseHelper = SqfliteHelper.instance;

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
