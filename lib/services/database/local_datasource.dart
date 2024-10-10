import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/services/database/data_source.dart';
import 'package:karakuri_agent/services/database/sqflite_helper.dart';
import 'package:karakuri_agent/utils/log.dart';

class LocalDatasource implements DataSource {
  final SqfliteHelper _databaseHelper = SqfliteHelper.instance;

  @override
  Future<bool> saveServiceConfigs(List<ServiceConfig> serviceConfigs) async {
    try {
      await _databaseHelper.saveServiceConfigs(serviceConfigs);
      return true;
    } catch (e) {
      debugPrint('Error creating serviceConfig: $e');
      return false;
    }
  }

  @override
  Future<List<ServiceConfig>> getServiceConfigs() async {
    try {
      return await _databaseHelper.getServiceConfigs();
    } catch (e) {
      debugPrint('Error fetching all serviceConfig: $e');
      return [];
    }
  }

  @override
  Future<void> close() async => await _databaseHelper.close();
}
