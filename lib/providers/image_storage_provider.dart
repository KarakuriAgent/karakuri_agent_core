import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/repositories/image_storage_repository.dart';
import 'package:karakuri_agent/services/image_storage/export_image_storage_service.dart';

final imageStorageProvider =
    FutureProvider.autoDispose<ImageStorageRepository>((ref) async {
  final ImageStorageService imageStorageService = ImageStorageService();
  await imageStorageService.init();
  final imageRepository = ImageStorageRepository(imageStorageService);
  // ref.onDispose(() {
  //   imageService.dispose();
  // });
  return imageRepository;
});
