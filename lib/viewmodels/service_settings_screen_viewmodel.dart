import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/repositories/config_storage_repository.dart';
import 'package:karakuri_agent/models/service_config.dart';

class ServiceSettingsScreenViewmodel {
  final Ref _ref;
  final ConfigStorageRepository _configStorage;
  final serviceConfigsProvider =
      StateProvider<List<ServiceConfig>?>((ref) => null);

  ServiceSettingsScreenViewmodel(this._ref, this._configStorage);

  Future<void> build() async {
    _ref.read(serviceConfigsProvider.notifier).state =
        await _configStorage.loadConfigs();
  }

  void dispose() {
    _ref.read(serviceConfigsProvider.notifier).dispose();
  }

  Future<void> addServiceConfig(ServiceConfig config) async {
    final id = await _configStorage.addServiceConfig(config);
    final serviceConfigNotifer = _ref.read(serviceConfigsProvider.notifier);
    final currentConfigs = serviceConfigNotifer.state ?? [];
    final updatedConfigs = [...currentConfigs, config.copyWith(id: id)];
    serviceConfigNotifer.state = updatedConfigs;
  }

  Future<void> updateServiceConfig(ServiceConfig config) async {
    final bool updated = await _configStorage.updateServiceConfig(config);
    if (updated) {
      final serviceConfigNotifer = _ref.read(serviceConfigsProvider.notifier);
      final currentConfigs = serviceConfigNotifer.state ?? [];
      final updatedConfigs = currentConfigs
          .map((c) => c.id == config.id ? config : c)
          .toList();
      serviceConfigNotifer.state = updatedConfigs;
    } else {
      throw Exception("Failed to update service config");
    }
  }

  Future<void> deleteServiceConfig(int configId) async {
    final bool deleted = await _configStorage.deleteServiceConfig(configId);
    if (deleted) {
      final serviceConfigNotifer = _ref.read(serviceConfigsProvider.notifier);
      final currentConfigs = serviceConfigNotifer.state ?? [];
      currentConfigs.removeWhere((c) => c.id == configId);
      serviceConfigNotifer.state = [...currentConfigs];
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
}
