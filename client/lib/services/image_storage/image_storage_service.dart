// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
abstract class ImageStorageService {
  static const String aiRoboImageName = 'ai_robo';
  static const String assetPath = 'assets/images/$aiRoboImageName.zip';
  Future<void> init();
  Future<void> saveImageZip({
    required String key,
    required List<int> file,
  });
  Future<List<int>> getImageZip(String key);
  Future<List<String>> getImageNames();
}
