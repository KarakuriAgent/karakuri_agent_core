import 'package:flutter/material.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/repositories/config_storage_repository.dart';

class HomeScreenViewModel extends ChangeNotifier {
  final ConfigStorageRepository _configStorage;
  bool initialized = false;
  List<AgentConfig> agentConfigs = [];
  HomeScreenViewModel(this._configStorage);

  Future<void> initialize() async {
    agentConfigs = await _configStorage.loadAgentConfigs();
    initialized = true;
    notifyListeners();
  }

  Future<void> addAgentConfig(AgentConfig config) async {
    final id = await _configStorage.addAgentConfig(config);
    if (id != -1) {
      agentConfigs = [...agentConfigs, config.copyWith(id: id)];
      notifyListeners();
    } else {
      throw Exception("Failed to add agent config");
    }
  }

  Future<void> updateAgentConfig(AgentConfig config) async {
    final bool updated = await _configStorage.updateAgentConfig(config);
    if (updated) {
      agentConfigs =
          agentConfigs.map((c) => c.id == config.id ? config : c).toList();
      notifyListeners();
    } else {
      throw Exception("Failed to update agent config");
    }
  }

  Future<void> deleteAgentConfig(int configId) async {
    final bool deleted = await _configStorage.deleteAgentConfig(configId);
    if (deleted) {
      agentConfigs = agentConfigs.where((c) => c.id != configId).toList();
      notifyListeners();
    } else {
      throw Exception("Failed to delete agent config");
    }
  }
}
