import 'package:flutter/material.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/repositories/config_storage_repository.dart';
import 'package:karakuri_agent/utils/exception.dart';

class HomeScreenViewModel extends ChangeNotifier {
  final ConfigStorageRepository _configStorage;
  bool _initialized = false;
  List<AgentConfig> _agentConfigs = [];

  bool get initialized => _initialized;
  List<AgentConfig> get agentConfigs => _agentConfigs;

  HomeScreenViewModel(this._configStorage);

  Future<void> initialize() async {
    _agentConfigs = await _configStorage.loadAgentConfigs();
    _initialized = true;
    notifyListeners();
  }

  Future<void> addAgentConfig(AgentConfig config) async {
    _ensureInitialized();
    final id = await _configStorage.addAgentConfig(config);
    if (id != -1) {
      _agentConfigs = [...agentConfigs, config.copyWith(id: id)];
      notifyListeners();
    } else {
      throw Exception("Failed to add agent config");
    }
  }

  Future<void> updateAgentConfig(AgentConfig config) async {
    _ensureInitialized();
    final bool updated = await _configStorage.updateAgentConfig(config);
    if (updated) {
      _agentConfigs =
          agentConfigs.map((c) => c.id == config.id ? config : c).toList();
      notifyListeners();
    } else {
      throw Exception("Failed to update agent config");
    }
  }

  Future<void> deleteAgentConfig(int configId) async {
    _ensureInitialized();
    final bool deleted = await _configStorage.deleteAgentConfig(configId);
    if (deleted) {
      _agentConfigs = agentConfigs.where((c) => c.id != configId).toList();
      notifyListeners();
    } else {
      throw Exception("Failed to delete agent config");
    }
  }

  void _ensureInitialized() {
    if (!initialized) {
      throw UninitializedException(runtimeType.toString());
    }
  }
}
