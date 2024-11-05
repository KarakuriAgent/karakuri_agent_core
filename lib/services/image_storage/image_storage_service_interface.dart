abstract class ImageStorageServiceInterface {
  Future<void> init();
  Future<void> saveImagZip({
    required String key,
    required List<int> file,
  });
  Future<List<int>> getImageZip(String key);
  Future<List<String>> getImageNames();
}
