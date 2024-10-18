import 'dart:typed_data';

import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/repositories/voice_activity_detaction_repository.dart';
import 'package:karakuri_agent/services/silero_vad/export_silero_vad_service.dart';

final _sileroVadServiceProvider = Provider.autoDispose((ref) {
  return SileroVadServce();
});

final voiceActivityDetectionProvider = FutureProvider.autoDispose
    .family<VoiceActivityDetectionRepository, Function(Uint8List)>(
        (ref, onAudio) async {
  final sileroVadService = ref.watch(_sileroVadServiceProvider);
  final voiceActivityDetection =
      VoiceActivityDetectionRepository(sileroVadService);
  await voiceActivityDetection.init(onAudio);
  ref.onDispose(() {
    voiceActivityDetection.destroy();
  });
  return voiceActivityDetection;
});
