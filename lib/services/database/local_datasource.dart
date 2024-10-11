import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/services/database/data_source.dart';
import 'package:karakuri_agent/services/database/sqflite_helper.dart';

class LocalDatasource implements DataSource {
  final SqfliteHelper _databaseHelper = SqfliteHelper.instance;

  @override
  Future<bool> saveServiceConfigs(List<ServiceConfig> serviceConfigs) async {
      await _databaseHelper.saveServiceConfigs(serviceConfigs);
      return true;
  }

  @override
  Future<List<ServiceConfig>> getServiceConfigs() async {
      return await _databaseHelper.getServiceConfigs();
  }

  @override
  Future<void> close() async => await _databaseHelper.close();
}
