import 'package:karakuri_agent/services/image_storage/image_storage_service_interface.dart';

class ImageStorageService extends ImageStorageServiceInterface {
  @override
  Future<void> init() async {}

  @override
  Future<void> saveImageZip({
    required String key,
    required List<int> file,
  }) async {}

  @override
  Future<List<int>> getImageZip(String key) async {
    return [];
  }

  @override
  Future<List<String>> getImageNames() async {
    return [];
  }
}
