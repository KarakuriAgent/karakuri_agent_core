abstract class ImageStorageServiceInterface {
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
