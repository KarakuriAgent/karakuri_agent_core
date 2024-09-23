import 'dart:convert';

import 'package:karakuri_agent/models/service_config.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ConfigStorage {
  static const String _keyServiceConfig = 'service_configs';
  final _prefs = SharedPreferencesAsync();

  Future<void> saveConfigs(List<ServiceConfig> configs) async {
    final jsonList =
        configs.map((config) => jsonEncode(config.toJson())).toList();
    await _prefs.setStringList(_keyServiceConfig, jsonList);
  }

  Future<List<ServiceConfig>> loadConfigs() async {
    final jsonList = await _prefs.getStringList(_keyServiceConfig) ?? [];
    return jsonList
        .map((jsonString) => ServiceConfig.fromJson(jsonDecode(jsonString)))
        .toList();
  }
}
