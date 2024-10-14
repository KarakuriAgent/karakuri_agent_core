import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/providers/config_storage_provider.dart';
import 'package:karakuri_agent/viewmodels/service_config_screen_viewmodel.dart';
import 'package:karakuri_agent/viewmodels/service_settings_screen_viewmodel.dart';

final serviceSettingsScreenViewmodelProvider =
    ChangeNotifierProvider.autoDispose((ref) {
  final configStorage = ref.watch(configStorageProvider);
  final viewModel = ServiceSettingsScreenViewmodel(configStorage);
  Future.microtask(() async {
    await viewModel.build();
  });
  return viewModel;
});

final serviceConfigScreenViewmodelProvider = ChangeNotifierProvider.autoDispose
    .family<ServiceConfigScreenViewmodel, ServiceConfig?>((ref, param) {
  return ServiceConfigScreenViewmodel(serviceConfig: param);
});
