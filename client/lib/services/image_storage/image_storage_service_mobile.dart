// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'dart:io';

import 'package:flutter/services.dart';

import 'package:karakuri_agent/services/image_storage/image_storage_service.dart';
import 'package:karakuri_agent/utils/exception.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;

class ImageStorageServiceImpl extends ImageStorageService {
  Future<String> get _imagesPath async =>
      '${(await getApplicationSupportDirectory()).path}/images';

  @override
  Future<void> init() async {
    try {
      final keys = await getImageNames();
      if (keys.contains(ImageStorageService.aiRoboImageName)) {
        return;
      }
      final data =
          await rootBundle.load(ImageStorageService.assetPath);
      final bytes =
          data.buffer.asUint8List(data.offsetInBytes, data.lengthInBytes);
      await saveImageZip(
        key: ImageStorageService.aiRoboImageName,
        file: bytes,
      );
    } catch (e) {
      throw ServiceException(
        runtimeType.toString(),
        'init',
        message: 'Failed to initialize default image: $e',
      );
    }
  }

  @override
  Future<void> saveImageZip({
    required String key,
    required List<int> file,
  }) async {
    try {
      await _ensureDirectoryExists();
      await File('${await _imagesPath}/$key.zip').writeAsBytes(file);
    } catch (e) {
      throw ServiceException(runtimeType.toString(), 'saveImageZip',
          message: 'Failed to save file: $e');
    }
  }

  @override
  Future<List<int>> getImageZip(String key) async {
    try {
      await _ensureDirectoryExists();
      return await File('${await _imagesPath}/$key.zip').readAsBytes();
    } catch (e) {
      throw ServiceException(runtimeType.toString(), 'getImageZip',
          message: 'Failed to load file: $e');
    }
  }

  @override
  Future<List<String>> getImageNames() async {
    final folder = await _ensureDirectoryExists();
    return await folder
        .list()
        .where((file) => file.path.endsWith('.zip'))
        .map((file) => p.basenameWithoutExtension(file.path))
        .toList();
  }

  Future<Directory> _ensureDirectoryExists() async {
    final folder = Directory(await _imagesPath);
    if (!await folder.exists()) {
      await folder.create(recursive: true);
    }
    return folder;
  }
}
