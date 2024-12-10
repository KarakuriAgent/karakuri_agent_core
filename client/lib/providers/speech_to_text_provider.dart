// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/repositories/speech_to_text_repository.dart';
import 'package:karakuri_agent/services/speech_to_text/speech_to_text_device_service.dart';

final speechToTextProvider =
    FutureProvider.autoDispose<SpeechToTextRepository>((ref) async {
  final speechToTextRepository = SpeechToTextRepository(SpeechToTextDeviceService());
  await speechToTextRepository.init();
  ref.onDispose(() async {
    await speechToTextRepository.dispose();
  });
  return speechToTextRepository;
});
