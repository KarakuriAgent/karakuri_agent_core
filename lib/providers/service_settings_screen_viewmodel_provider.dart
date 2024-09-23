import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/providers/config_storage_provider.dart';
import 'package:karakuri_agent/viewmodels/service_settings_screen_viewmodel.dart';

final serviceSettingsScreenViewmodelProvider = Provider.autoDispose((ref) {
  final configStorage = ref.watch(configStorageProvider);
  final viewModel = ServiceSettingsScreenViewmodel(ref, configStorage);
  Future.microtask(() async {
    await viewModel.build();
  });
  ref.onDispose(() {
    viewModel.dispose();
  });
  return viewModel;
});
