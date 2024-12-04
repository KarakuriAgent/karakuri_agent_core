import 'dart:async';
import 'dart:convert';

import 'package:archive/archive.dart';
import 'package:flutter/foundation.dart';
import 'package:karakuri_agent/models/agent_image.dart';
import 'package:karakuri_agent/models/agent_responce.dart';
import 'package:karakuri_agent/services/image_storage/image_storage_service.dart';
import 'package:karakuri_agent/utils/exception.dart';

class ImageStorageRepository {
  final ImageStorageService _imageStorageService;

  ImageStorageRepository(this._imageStorageService);

  Future<List<String>> getImageNames() async {
    return await _imageStorageService.getImageNames();
  }

  Future<List<AgentImage>> getAgentImages(String imageName) async {
    final imageZip = await _imageStorageService.getImageZip(imageName);
    return _loadImages(imageZip);
  }

  Future<List<AgentImage>> _loadImages(List<int> imageZip) async {
    final archive = ZipDecoder().decodeBytes(imageZip);
    Map<String, dynamic> settings = {};
    Map<String, Uint8List> images = {};
    for (var archiveFile in archive.files) {
      if (archiveFile.isFile) {
        if (archiveFile.name == "settings.json") {
          String jsonString = utf8.decode(archiveFile.content);
          settings = jsonDecode(jsonString);
        } else {
          images[archiveFile.name] = Uint8List.fromList(archiveFile.content);
        }
      }
    }
    if (settings.isEmpty) {
      throw RepositoryException(runtimeType.toString(), '_loadImages',
          message: 'settings.json is empty');
    }
    if (images.isEmpty) {
      throw RepositoryException(runtimeType.toString(), '_loadImages',
          message: 'images is empty');
    }
    List<AgentImage> agentImages = [];
    for (var emotion in settings.keys) {
      agentImages.add(
        AgentImage(
          emotion: Emotion.fromString(emotion),
          extension: (settings[emotion]! as String).split('.').last,
          image: images[settings[emotion]]!,
        ),
      );
    }
    return agentImages;
  }
}
