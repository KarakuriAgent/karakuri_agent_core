import 'package:karakuri_agent/models/service_config.dart';

abstract class DataSource {
  Future<int> insertServiceConfig(ServiceConfig serviceConfig);
  Future<bool> updateServiceConfig(ServiceConfig serviceConfig);
  Future<bool> deleteServiceConfig(int configId);
  Future<List<ServiceConfig>> queryAllServiceConfig();
  Future<void> close();
}
