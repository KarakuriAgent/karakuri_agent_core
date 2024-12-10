// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/repositories/image_storage_repository.dart';
import 'package:karakuri_agent/services/image_storage/export_image_storage_service.dart';
import 'package:karakuri_agent/services/image_storage/image_storage_service.dart';
import 'package:karakuri_agent/utils/exception.dart';

final imageStorageProvider =
    FutureProvider.autoDispose<ImageStorageRepository>((ref) async {
  try {
    final ImageStorageService imageStorageService = ImageStorageServiceImpl();
    await imageStorageService.init();
    final imageRepository = ImageStorageRepository(imageStorageService);
    return imageRepository;
  } catch (e) {
    throw ProviderException('imageStorageProvider', message: 'Failed to initialize image storage: $e');
  }
});
