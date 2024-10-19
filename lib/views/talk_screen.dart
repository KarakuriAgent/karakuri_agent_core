import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/providers/viewmodel_providers.dart';
import 'package:karakuri_agent/viewmodels/talk_screen_view_model.dart';
import 'package:karakuri_agent/i18n/strings.g.dart';

class TalkScreen extends HookConsumerWidget {
  final AgentConfig _agentConfig;
  const TalkScreen(this._agentConfig, {super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.listen<TalkScreenViewModel>(
      talkScreenViewModelProvider(_agentConfig),
      (_, __) {},
    );
    final initialized = ref.watch(talkScreenViewModelProvider(_agentConfig)
        .select((it) => it.initialized));
    if (!initialized) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    } else {
      return _TalkContent(
        agentConfig: _agentConfig,
      );
    }
  }
}

class _TalkContent extends HookConsumerWidget {
  final AgentConfig agentConfig;

  const _TalkContent({required this.agentConfig});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final viewModel = ref.read(talkScreenViewModelProvider(agentConfig));
    final isListening = ref.watch(
        talkScreenViewModelProvider(agentConfig).select((it) => it.isListening));
    final text = ref.watch(talkScreenViewModelProvider(agentConfig)
        .select((it) => it.resultText));
    return Scaffold(
      appBar: AppBar(
        title: Text(t.talk.title),
      ),
      body: SingleChildScrollView(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(text),
            ElevatedButton(
              onPressed: () {
                if (isListening) {
                  viewModel.pause();
                } else {
                  viewModel.start();
                }
              },
              child: Text(isListening ? t.talk.pause : t.talk.start),
            ),
          ],
        ),
      ),
    );
  }
}
