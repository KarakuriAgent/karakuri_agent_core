// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/repositories/config_storage_repository.dart';
import 'package:karakuri_agent/services/database/local_datasource.dart';

final _localStolageProvider = Provider.autoDispose((ref) {
  final datasource = LocalDatasource();
 ref.onDispose(() async {
    await datasource.close();
  });
  return datasource;
});

final configStorageProvider = Provider.autoDispose((ref) {
  final stolage = ref.watch(_localStolageProvider);
  return ConfigStorageRepository(stolage);
});
