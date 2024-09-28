import 'dart:convert';

import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/services/shared_preference_service.dart';

class ConfigStorageRepository {
  static const String _keyServiceConfig = 'service_configs';
  final SharedPreferencesService _service;

  ConfigStorageRepository(this._service);

  Future<void> saveConfigs(List<ServiceConfig> configs) async {
    final jsonList =
        configs.map((config) => jsonEncode(config.toJson())).toList();
    await _service.setStringList(_keyServiceConfig, jsonList);
  }

  Future<List<ServiceConfig>> loadConfigs() async {
    final jsonList = await _service.getStringList(_keyServiceConfig) ?? [];
    return jsonList
        .map((jsonString) => ServiceConfig.fromJson(jsonDecode(jsonString)))
        .toList();
  }
}
