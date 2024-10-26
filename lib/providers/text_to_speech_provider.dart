import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/repositories/text_to_speech_repository.dart';

final textToSpeechProvider = Provider.autoDispose
    .family<TextToSpeechRepository, AgentConfig>((ref, agentConfig) {
  final textToSpeechRepository = TextToSpeechRepository(agentConfig);
  ref.onDispose(() {
    textToSpeechRepository.dispose();
  });
  return textToSpeechRepository;
});
