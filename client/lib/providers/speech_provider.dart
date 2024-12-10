import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/repositories/speech_repository.dart';
import 'package:karakuri_agent/services/speech/speech_audio_player_service.dart';

final speechProvider = Provider.autoDispose<SpeechRepository>((ref) {
  final speechRepository = SpeechRepository(SpeechAudioPlayerService());
  ref.onDispose(() async {
    await speechRepository.dispose();
  });
  return speechRepository;
});
