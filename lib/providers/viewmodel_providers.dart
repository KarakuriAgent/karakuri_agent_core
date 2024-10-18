import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/providers/config_storage_provider.dart';
import 'package:karakuri_agent/viewmodels/agent_config_screen_viewmodel.dart';
import 'package:karakuri_agent/viewmodels/home_screen_viewmodel.dart';
import 'package:karakuri_agent/viewmodels/service_config_screen_viewmodel.dart';
import 'package:karakuri_agent/viewmodels/service_settings_screen_viewmodel.dart';
import 'package:karakuri_agent/viewmodels/talk_screen_view_model.dart';

final homeScreenViewModelProvider = ChangeNotifierProvider.autoDispose((ref) {
  final configStorage = ref.watch(configStorageProvider);
  final viewModel = HomeScreenViewModel(configStorage);
  Future.microtask(() async {
    await viewModel.build();
  });
  return viewModel;
});

final agentConfigScreenViewmodelProvider = ChangeNotifierProvider.autoDispose
    .family<AgentConfigScreenViewmodel, AgentConfig?>((ref, param) {
  final configStorage = ref.watch(configStorageProvider);
  final viewModel =
      AgentConfigScreenViewmodel(configStorage, agentConfig: param);
  Future.microtask(() async {
    await viewModel.build();
  });
  return viewModel;
});

final talkScreenViewModelProvider = ChangeNotifierProvider.autoDispose
    .family<TalkScreenViewModel, AgentConfig>((ref, agentConfig) {
  final viewModel = TalkScreenViewModel(ref, agentConfig);
  Future.microtask(() async {
    await viewModel.build();
  });
  ref.onDispose(() {
    viewModel.dispose();
  });
  return viewModel;
});

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
