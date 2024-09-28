import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/utils/voice_activity_detaction/export_voice_activity_detaction.dart';

final voiceActivityDetectionProvider = FutureProvider.autoDispose
    .family<VoiceActivityDetection, Function(List<int>)>((ref, onAudio) async {
  final voiceActivityDetection = VoiceActivityDetection();
  await voiceActivityDetection.init(onAudio);
  ref.onDispose(() {
    voiceActivityDetection.destroy();
  });
  return voiceActivityDetection;
});
