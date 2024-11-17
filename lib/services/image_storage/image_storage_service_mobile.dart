import 'dart:io';

import 'package:flutter/services.dart';

import 'package:karakuri_agent/services/image_storage/image_storage_service_interface.dart';
import 'package:karakuri_agent/utils/exception.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;

class ImageStorageService extends ImageStorageServiceInterface {
  Future<String> get _imagesPath async =>
      '${(await getApplicationSupportDirectory()).path}/images';

  @override
  Future<void> init() async {
    if (await getImageNames().then((keys) =>
        keys.contains(ImageStorageServiceInterface.aiRoboImageName))) {
      return;
    }
    final data = await rootBundle.load(ImageStorageServiceInterface.assetPath);
    final bytes =
        data.buffer.asUint8List(data.offsetInBytes, data.lengthInBytes);
    await saveImageZip(key: ImageStorageServiceInterface.aiRoboImageName, file: bytes);
  }

  @override
  Future<void> saveImageZip({
    required String key,
    required List<int> file,
  }) async {
    try {
      final folder = Directory(await _imagesPath);
      if (!await folder.exists()) {
        await folder.create(recursive: true);
      }
      await File('${await _imagesPath}/$key.zip').writeAsBytes(file);
    } catch (e) {
      throw ServiceException(runtimeType.toString(), 'saveImageZip',
          message: 'Failed to save file: $e');
    }
  }

  @override
  Future<List<int>> getImageZip(String key) async {
    try {
      final folder = Directory(await _imagesPath);
      if (!await folder.exists()) {
        await folder.create(recursive: true);
      }
      return await File('${await _imagesPath}/$key.zip').readAsBytes();
    } catch (e) {
      throw ServiceException(runtimeType.toString(), 'getImageZip',
          message: 'Failed to load file: $e');
    }
  }

  @override
  Future<List<String>> getImageNames() async {
    final folder = Directory(await _imagesPath);
    if (!await folder.exists()) {
      await folder.create(recursive: true);
    }
    return await folder
        .list()
        .map((file) => p.basenameWithoutExtension(file.path))
        .toList();
  }
}
