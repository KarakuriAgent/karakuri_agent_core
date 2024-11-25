import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/repositories/text_repository.dart';

final textProvider = Provider.autoDispose
    .family<TextRepository, AgentConfig>((ref, agentConfig) {
  final textRepository = TextRepository(agentConfig);
  ref.onDispose(() {
    textRepository.dispose();
  });
  return textRepository;
});
