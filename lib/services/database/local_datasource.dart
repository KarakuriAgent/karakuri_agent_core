import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/services/database/data_source.dart';
import 'package:karakuri_agent/services/database/sqflite_helper.dart';

class LocalDatasource implements DataSource {
  final SqfliteHelper _databaseHelper = SqfliteHelper.instance;

  @override
  Future<int> insertServiceConfig(ServiceConfig serviceConfig) async {
      return await _databaseHelper.insertServiceConfig(serviceConfig);
  }

  @override
  Future<bool> updateServiceConfig(ServiceConfig serviceConfig) async {
      return await _databaseHelper.updateServiceConfig(serviceConfig);
  }

  @override
  Future<bool> deleteServiceConfig(int configId) async {
      return await _databaseHelper.deleteServiceConfig(configId);
  }

  @override
  Future<List<ServiceConfig>> queryAllServiceConfig() async {
      return await _databaseHelper.queryAllServiceConfig();
  }

  @override
  Future<void> close() async => await _databaseHelper.close();
}
