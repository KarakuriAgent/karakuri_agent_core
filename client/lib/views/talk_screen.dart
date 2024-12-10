// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/providers/view_model_providers.dart';
import 'package:karakuri_agent/view_models/talk_screen_view_model.dart';
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
    final state = ref.watch(
        talkScreenViewModelProvider(_agentConfig).select((it) => it.state));
    if (state == TalkScreenViewModelState.loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    } else {
      return _TalkContent(
        agentConfig: _agentConfig,
        state: state,
      );
    }
  }
}

class _TalkContent extends HookConsumerWidget {
  final AgentConfig agentConfig;
  final TalkScreenViewModelState state;

  const _TalkContent({required this.agentConfig, required this.state});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final viewModel = ref.read(talkScreenViewModelProvider(agentConfig));
    final (agentImage, userMessage, agentMessage, emotion) = ref.watch(
      talkScreenViewModelProvider(agentConfig).select(
        (it) =>
            (it.agentImage, it.userMessage, it.agentMessage, it.emotion),
      ),
    );
    return Scaffold(
      appBar: AppBar(
        title: Text(t.talk.title),
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text("User: $userMessage"),
          Text("Agent: $agentMessage"),
          Text("Emotion: $emotion"),
          if (agentImage != null)
            ConstrainedBox(
              constraints: BoxConstraints(
                maxWidth: MediaQuery.of(context).size.width * 0.3,
                maxHeight: MediaQuery.of(context).size.width * 0.3,
              ),
              child: Builder(
                builder: (context) {
                  try {
                    return agentImage.extension.toLowerCase() == 'svg'
                        ? SvgPicture.memory(
                            agentImage.image,
                            fit: BoxFit.contain,
                          )
                        : Image.memory(
                            agentImage.image,
                            fit: BoxFit.contain,
                          );
                  } catch (e) {
                    debugPrint('Error loading image: $e');
                    return const Icon(Icons.error);
                  }
                },
              ),
            ),
          ElevatedButton(
            onPressed: () async {
              try {
                if (state == TalkScreenViewModelState.initialized) {
                  await viewModel.start();
                } else {
                  await viewModel.stop();
                }
              } catch (e) {
                if (!context.mounted) return;
                debugPrint(e.toString());
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                      content: Text(
                          state == TalkScreenViewModelState.initialized
                              ? t.talk.error.startFailed
                              : t.talk.error.pauseFailed)),
                );
              }
            },
            child: Text(state == TalkScreenViewModelState.initialized
                ? t.talk.start
                : t.talk.pause),
          ),
        ],
      ),
    );
  }
}
