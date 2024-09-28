import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/repositories/config_storage_repository.dart';
import 'package:karakuri_agent/services/shared_preference_service.dart';

final _sharedPreferencesServiceProvider = Provider.autoDispose((ref) {
  return SharedPreferencesService();
});

final configStorageProvider = Provider.autoDispose((ref) {
  final prefsService = ref.watch(_sharedPreferencesServiceProvider);
  return ConfigStorageRepository(prefsService);
});
