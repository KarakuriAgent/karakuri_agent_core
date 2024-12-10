// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/providers/view_model_providers.dart';
import 'package:karakuri_agent/view_models/home_screen_view_model.dart';
import 'package:karakuri_agent/views/agent_config_screen.dart';
import 'package:karakuri_agent/i18n/strings.g.dart';
import 'package:karakuri_agent/views/talk_screen.dart';

class HomeScreen extends HookConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.listen<HomeScreenViewModel>(
      homeScreenViewModelProvider,
      (_, __) {},
    );
    final viewModel = ref.read(homeScreenViewModelProvider);
    final initialized =
        ref.watch(homeScreenViewModelProvider.select((it) => it.initialized));
    return Scaffold(
      appBar: AppBar(
        title: Text(t.home.title),
      ),
      body: !initialized
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: <Widget>[
                  _AgentContent(viewModel: viewModel)
                ],
              ),
            ),
    );
  }
}

class _AgentContent extends HookConsumerWidget {
  final HomeScreenViewModel viewModel;

  const _AgentContent({required this.viewModel});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final configs =
        ref.watch(homeScreenViewModelProvider.select((it) => it.agentConfigs));
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        ...configs.map((config) => _AgentCard(config: config)),
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: OutlinedButton(
            child: Text(t.home.agent.addAgent),
            onPressed: () async {
              final agentConfig = await Navigator.push(
                context,
                CupertinoPageRoute(
                  builder: (context) => const AgentConfigScreen(),
                ),
              ) as AgentConfig?;
              if (agentConfig != null) {
                viewModel.addAgentConfig(agentConfig);
              }
            },
          ),
        ),
      ],
    );
  }
}

class _AgentCard extends HookConsumerWidget {
  final AgentConfig config;

  const _AgentCard({required this.config});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final viewModel = ref.read(homeScreenViewModelProvider);
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              t.home.agent.name(name: config.name),
            ),
            Row(
              children: [
                TextButton(
                  child: Text(t.home.agent.startTalk),
                  onPressed: () async {
                    await Navigator.push(
                      context,
                      CupertinoPageRoute(
                        builder: (context) => TalkScreen(config),
                      ),
                    );
                  },
                ),
                TextButton(
                  child: Text(t.home.agent.editAgent),
                  onPressed: () async {
                    final agentConfig = await Navigator.push(
                      context,
                      CupertinoPageRoute(
                        builder: (context) =>
                            AgentConfigScreen(initialConfig: config),
                      ),
                    ) as AgentConfig?;
                    if (agentConfig != null) {
                      viewModel.updateAgentConfig(agentConfig);
                    }
                  },
                ),
                TextButton(
                  child: Text(t.home.agent.deleteAgent),
                  onPressed: () async {
                    if (config.id != null) {
                      viewModel.deleteAgentConfig(config.id!);
                    }
                  },
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
