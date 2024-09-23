import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/utils/config_storage.dart';
import 'package:karakuri_agent/models/service_config.dart';

class ServiceSettingsScreenViewmodel {
  final Ref _ref;
  final ConfigStorage _configStorage;
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

  Future<void> saveServiceConfig(ServiceConfig config) async {
    final serviceConfigNotifer = _ref.read(serviceConfigsProvider.notifier);
    final currentConfigs = serviceConfigNotifer.state ?? [];
    final index = currentConfigs.indexWhere((c) => c.id == config.id);
    List<ServiceConfig> updatedConfigs;

    if (index != -1) {
      updatedConfigs = List.from(currentConfigs);
      updatedConfigs[index] = config;
    } else {
      updatedConfigs = [
        ...currentConfigs,
        config.copyWith(id: DateTime.now().millisecondsSinceEpoch.toString())
      ];
    }

    serviceConfigNotifer.state = updatedConfigs;
    await _configStorage.saveConfigs(updatedConfigs);
  }

  Future<void> deleteServiceConfig(String configId) async {
    final serviceConfigNotifer = _ref.read(serviceConfigsProvider.notifier);
    final currentConfigs = serviceConfigNotifer.state ?? [];
    final updatedConfigs =
        currentConfigs.where((config) => config.id != configId).toList();
    serviceConfigNotifer.state = updatedConfigs;
    await _configStorage.saveConfigs(updatedConfigs);
  }

  List<String> getConfigTypes(ServiceConfig config) {
    List<String> types = [];
    if (config.textConfig != null) types.add("TEXT");
    if (config.ttsConfig != null) types.add("TEXT TO SPEECH");
    if (config.sttConfig != null) types.add("SPEECH TO TEXT");
    return types;
  }
}
