import 'package:karakuri_agent/models/service_config.dart';

abstract class DataSource {
  Future<bool> saveServiceConfigs(List<ServiceConfig> serviceConfigs);
  Future<List<ServiceConfig>> getServiceConfigs();
  Future<void> close();
}
