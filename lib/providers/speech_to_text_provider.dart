import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/repositories/speech_to_text_repository.dart';

final speechToTextProvider = FutureProvider.autoDispose
    .family<SpeechToTextRepository, (AgentConfig, Function(String))>((ref, param) async {
  final speechToTextRepository = SpeechToTextRepository(ref, param.$1, param.$2);
  await speechToTextRepository.init();
  ref.onDispose(() {
    speechToTextRepository.dispose();
  });
  return speechToTextRepository;
});
