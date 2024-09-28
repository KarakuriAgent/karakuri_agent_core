import 'package:shared_preferences/shared_preferences.dart';

class SharedPreferencesService {
  final _prefs = SharedPreferencesAsync();

  Future<void> setStringList(String key, List<String> value) async {
    await _prefs.setStringList(key, value);
  }

  Future<List<String>?> getStringList(String key) async {
    return await _prefs.getStringList(key);
  }
}
