import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/providers/config_storage_provider.dart';
import 'package:karakuri_agent/providers/image_storage_provider.dart';
import 'package:karakuri_agent/view_models/agent_config_screen_view_model.dart';
import 'package:karakuri_agent/view_models/home_screen_view_model.dart';
import 'package:karakuri_agent/view_models/service_config_screen_view_model.dart';
import 'package:karakuri_agent/view_models/service_settings_screen_view_model.dart';
import 'package:karakuri_agent/view_models/talk_screen_view_model.dart';

final homeScreenViewModelProvider = ChangeNotifierProvider.autoDispose((ref) {
  final configStorage = ref.watch(configStorageProvider);
  final viewModel = HomeScreenViewModel(configStorage);
  Future.microtask(() async {
    await viewModel.initialize();
  });
  return viewModel;
});

final agentConfigScreenViewModelProvider = ChangeNotifierProvider.autoDispose
    .family<AgentConfigScreenViewModel, AgentConfig?>((ref, param) {
  final configStorage = ref.watch(configStorageProvider);
  final viewModel =
      AgentConfigScreenViewModel(configStorage, agentConfig: param);
  Future.microtask(() async {
  final imageStorage = await ref.watch(imageStorageProvider.future);
    await viewModel.initialize(imageStorage);
  });
  return viewModel;
});

final talkScreenViewModelProvider = ChangeNotifierProvider.autoDispose
    .family<TalkScreenViewModel, AgentConfig>((ref, agentConfig) {
  final viewModel = TalkScreenViewModel(ref, agentConfig);
  Future.microtask(() async {
    await viewModel.initialize();
  });
  ref.onDispose(() {
    viewModel.dispose();
  });
  return viewModel;
});

final serviceSettingsScreenViewModelProvider =
    ChangeNotifierProvider.autoDispose((ref) {
  final configStorage = ref.watch(configStorageProvider);
  final viewModel = ServiceSettingsScreenViewModel(configStorage);
  Future.microtask(() async {
    await viewModel.initialize();
  });
  return viewModel;
});

final serviceConfigScreenViewModelProvider = ChangeNotifierProvider.autoDispose
    .family<ServiceConfigScreenViewModel, ServiceConfig?>((ref, param) {
  return ServiceConfigScreenViewModel(ref, serviceConfig: param);
});
