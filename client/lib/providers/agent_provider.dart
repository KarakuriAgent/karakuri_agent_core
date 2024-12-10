// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/repositories/agent_repository.dart';
import 'package:karakuri_agent/services/agent/karakuri_agent_service.dart';

final chatProvider = Provider.autoDispose
    .family<AgentRepository, AgentConfig>((ref, agentConfig) {
  final textRepository = AgentRepository(KarakuriAgentService(agentConfig));
  ref.onDispose(() async {
    await textRepository.dispose();
  });
  return textRepository;
});
