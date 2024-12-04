import 'package:flutter/services.dart';
import 'package:idb_shim/idb_browser.dart';
import 'package:karakuri_agent/services/image_storage/image_storage_service.dart';

import 'package:karakuri_agent/utils/exception.dart';

class ImageStorageServiceImpl extends ImageStorageService {
  static const String dbName = 'ImageStorage';
  static const int dbVersion = 1;
  static const String storeName = 'files';

  late IdbFactory _idbFactory;

  ImageStorageServiceImpl() {
    _idbFactory = getIdbFactory()!;
  }

  @override
  Future<void> init() async {
    if (await getImageNames().then((keys) =>
        keys.contains(ImageStorageService.aiRoboImageName))) {
      return;
    }
    final ByteData data =
        await rootBundle.load(ImageStorageService.assetPath);
    final List<int> bytes = data.buffer.asUint8List();
    await saveImageZip(
        key: ImageStorageService.aiRoboImageName, file: bytes);
  }

  Future<Database> _openDatabase() async {
    try {
      return await _idbFactory.open(dbName, version: dbVersion,
          onUpgradeNeeded: (VersionChangeEvent e) {
        Database db = e.database;
        if (!db.objectStoreNames.contains(storeName)) {
          db.createObjectStore(storeName);
        }
      });
    } catch (e) {
      throw ServiceException(runtimeType.toString(), '_openDatabase',
          message: 'Failed to open database: $e');
    }
  }

  @override
  Future<void> saveImageZip({
    required String key,
    required List<int> file,
  }) async {
    final db = await _openDatabase();
    try {
      final transaction = db.transaction(storeName, idbModeReadWrite);
      final store = transaction.objectStore(storeName);

      await store.put(file, key);
      await transaction.completed;
    } catch (e) {
      throw ServiceException(runtimeType.toString(), 'saveImageZip',
          message: 'Failed to save file: $e');
    } finally {
      db.close();
    }
  }

  @override
  Future<List<int>> getImageZip(String key) async {
    final db = await _openDatabase();
    try {
      final transaction = db.transaction(storeName, idbModeReadOnly);
      final store = transaction.objectStore(storeName);

      final data = await store.getObject(key);
      return data as List<int>;
    } catch (e) {
      throw ServiceException(runtimeType.toString(), 'getImageZip',
          message: 'Failed to load file: $e');
    } finally {
      db.close();
    }
  }

  @override
  Future<List<String>> getImageNames() async {
    final db = await _openDatabase();
    try {
      final transaction = db.transaction(storeName, idbModeReadOnly);
      final store = transaction.objectStore(storeName);

      final List<dynamic> keys = await store.getAllKeys();

      return keys.map((key) => key.toString()).toList();
    } catch (e) {
      throw ServiceException(runtimeType.toString(), 'getImageNames',
          message: 'Failed to get keys: $e');
    } finally {
      db.close();
    }
  }
}
