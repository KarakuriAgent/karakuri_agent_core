import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/services/database/local_datasource.dart';

class ConfigStorageRepository {
  final LocalDatasource _datasource;

  ConfigStorageRepository(this._datasource);

  Future<void> saveServiceConfigs(List<ServiceConfig> configs) async {
    await _datasource.saveServiceConfigs(configs);
  }

  Future<List<ServiceConfig>> loadConfigs() async {
    return await _datasource.getServiceConfigs();
  }
}
