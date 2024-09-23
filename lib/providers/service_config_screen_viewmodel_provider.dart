import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/viewmodels/service_config_screen_viewmodel.dart';

final serviceConfigScreenViewmodelProvider = Provider.autoDispose
    .family<ServiceConfigScreenViewmodel, ServiceConfig?>((ref, param) {
  return ServiceConfigScreenViewmodel(ref, serviceConfig: param);
});
