abstract class ImageStorageServiceInterface {
  Future<void> init();
  Future<void> saveImageZip({
    required String key,
    required List<int> file,
  });
  Future<List<int>> getImageZip(String key);
  Future<List<String>> getImageNames();
}
