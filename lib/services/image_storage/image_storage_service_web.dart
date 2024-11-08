import 'package:flutter/services.dart';
import 'package:idb_shim/idb_browser.dart';

import 'package:karakuri_agent/services/image_storage/image_storage_service_interface.dart';

class ImageStorageService extends ImageStorageServiceInterface {
  static const String dbName = 'ImageStorage';
  static const int dbVersion = 1;
  static const String storeName = 'files';
  static const String aiRoboImageName = 'ai_robo';
  static const String assetPath = 'images/$aiRoboImageName.zip';

  late IdbFactory _idbFactory;

  ImageStorageService() {
    _idbFactory = getIdbFactory()!;
  }

  @override
  Future<void> init() async {
    if (await getImageNames()
        .then((keys) => keys.contains(aiRoboImageName))) {
      return;
    }
    final ByteData data = await rootBundle.load(assetPath);
    final List<int> bytes = data.buffer.asUint8List();
    await saveImageZip(key: aiRoboImageName, file: bytes);
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
      throw 'Failed to open database: $e';
    }
  }

  @override
  Future<void> saveImageZip({
    required String key,
    required List<int> file,
  }) async {
    try {
      final db = await _openDatabase();
      final transaction = db.transaction(storeName, idbModeReadWrite);
      final store = transaction.objectStore(storeName);

      await store.put(file, key);
      await transaction.completed;
      db.close();
    } catch (e) {
      throw 'Failed to save file: $e';
    }
  }

  @override
  Future<List<int>> getImageZip(String key) async {
    try {
      final db = await _openDatabase();
      final transaction = db.transaction(storeName, idbModeReadOnly);
      final store = transaction.objectStore(storeName);

      final data = await store.getObject(key);
      db.close();

      return data as List<int>;
    } catch (e) {
      throw 'Failed to load file: $e';
    }
  }

  @override
  Future<List<String>> getImageNames() async {
    try {
      final db = await _openDatabase();
      final transaction = db.transaction(storeName, idbModeReadOnly);
      final store = transaction.objectStore(storeName);

      final List<dynamic> keys = await store.getAllKeys();
      db.close();

      return keys.map((key) => key.toString()).toList();
    } catch (e) {
      throw 'Failed to get keys: $e';
    }
  }
}
