
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/utils/config_storage.dart';

final configStorageProvider = Provider.autoDispose((ref) {
  return ConfigStorage();
});
