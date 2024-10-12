import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/services/database/local_datasource.dart';

class ConfigStorageRepository {
  final LocalDatasource _datasource;

  ConfigStorageRepository(this._datasource);

  Future<int> addServiceConfig(ServiceConfig config) async {
    return await _datasource.insertServiceConfig(config);
  }

  Future<bool> updateServiceConfig(ServiceConfig config) async {
    return await _datasource.updateServiceConfig(config);
  }

  Future<bool> deleteServiceConfig(int configId) async {
    return await _datasource.deleteServiceConfig(configId);
  }

  Future<List<ServiceConfig>> loadConfigs() async {
    return await _datasource.queryAllServiceConfig();
  }
}
