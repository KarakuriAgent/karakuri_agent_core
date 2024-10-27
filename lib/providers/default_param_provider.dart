import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/repositories/default_param_repository.dart';

final defaultParamProvider = Provider.autoDispose
    .family<DefaultParamRepository, ServiceType>((ref, serviceType) {
  return DefaultParamRepository(serviceType);
});
