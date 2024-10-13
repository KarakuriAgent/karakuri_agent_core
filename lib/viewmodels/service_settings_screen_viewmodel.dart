import 'package:flutter/cupertino.dart';
import 'package:karakuri_agent/repositories/config_storage_repository.dart';
import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/utils/exception.dart';

class ServiceSettingsScreenViewmodel extends ChangeNotifier {
  final ConfigStorageRepository _configStorage;
  List<ServiceConfig> serviceConfigs = [];
  bool initialized = false;

  ServiceSettingsScreenViewmodel(this._configStorage);

  Future<void> build() async {
    serviceConfigs = await _configStorage.loadConfigs();
    initialized = true;
    notifyListeners();
  }

  Future<void> addServiceConfig(ServiceConfig config) async {
    _ensureInitialized();
    final id = await _configStorage.addServiceConfig(config);
    if (id != -1) {
      serviceConfigs = [...serviceConfigs, config.copyWith(id: id)];
      notifyListeners();
    } else {
      throw Exception("Failed to add service config");
    }
  }

  Future<void> updateServiceConfig(ServiceConfig config) async {
    _ensureInitialized();
    final bool updated = await _configStorage.updateServiceConfig(config);
    if (updated) {
      serviceConfigs =
          serviceConfigs.map((c) => c.id == config.id ? config : c).toList();
      notifyListeners();
    } else {
      throw Exception("Failed to update service config");
    }
  }

  Future<void> deleteServiceConfig(int configId) async {
    _ensureInitialized();
    final bool deleted = await _configStorage.deleteServiceConfig(configId);
    if (deleted) {
      serviceConfigs = serviceConfigs.where((c) => c.id != configId).toList();
      notifyListeners();
    } else {
      throw Exception("Failed to delete service config");
    }
  }

  List<String> getConfigTypes(ServiceConfig config) {
    List<String> types = [];
    if (config.textConfig != null) types.add("TEXT");
    if (config.textToSpeechConfig != null) types.add("TEXT TO SPEECH");
    if (config.speechToTextConfig != null) types.add("SPEECH TO TEXT");
    return types;
  }

  void _ensureInitialized() {
    if (!initialized) {
      throw UninitializedViewModelException();
    }
  }
}
