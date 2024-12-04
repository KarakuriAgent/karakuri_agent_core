import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/i18n/strings.g.dart';
import 'package:karakuri_agent/providers/view_model_providers.dart';
import 'package:karakuri_agent/view_models/agent_config_screen_view_model.dart';

class AgentConfigScreen extends HookConsumerWidget {
  final AgentConfig? initialConfig;
  const AgentConfigScreen({super.key, this.initialConfig});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.listen<AgentConfigScreenViewModel>(
      agentConfigScreenViewModelProvider(initialConfig),
      (_, __) {},
    );
    final initialized = ref.watch(
        agentConfigScreenViewModelProvider(initialConfig)
            .select((it) => it.initialized));
    return Scaffold(
      appBar: AppBar(
        title: Text(initialConfig == null
            ? t.agentConfig.agentAdd
            : t.agentConfig.agentEdit),
      ),
      body: !initialized
          ? const Center(child: CircularProgressIndicator())
          : _AgentConfigContent(initialConfig: initialConfig),
    );
  }
}

class _AgentConfigContent extends HookConsumerWidget {
  final AgentConfig? initialConfig;
  const _AgentConfigContent({required this.initialConfig});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final (
      nameController,
      baseUrlController,
      apiKeyController,
      agentIdController
    ) = ref
        .read(agentConfigScreenViewModelProvider(initialConfig).select((it) => (
              it.nameController,
              it.baseUrlController,
              it.apiKeyController,
              it.agentIdController
            )));
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          TextFormField(
            controller: nameController,
            decoration: InputDecoration(labelText: t.agentConfig.name),
          ),
          TextFormField(
            controller: baseUrlController,
            decoration: InputDecoration(labelText: t.agentConfig.baseUrl),
          ),
          TextFormField(
            controller: apiKeyController,
            decoration: InputDecoration(labelText: t.agentConfig.apiKey),
          ),
          TextFormField(
            controller: agentIdController,
            decoration: InputDecoration(labelText: t.agentConfig.agentId),
          ),
          _ImageKeySection(initialConfig: initialConfig),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: () => _saveConfig(context, ref, initialConfig),
            child: Text(t.agentConfig.save),
          ),
        ],
      ),
    );
  }

  void _saveConfig(
    BuildContext context,
    WidgetRef ref,
    AgentConfig? initialConfig,
  ) {
    final viewModel =
        ref.read(agentConfigScreenViewModelProvider(initialConfig));
    final error = viewModel.validationCheck();
    if (error != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(error),
      ));
      return;
    }
    Navigator.of(context).pop(viewModel.createAgentConfig());
  }
}

class _ImageKeySection extends HookConsumerWidget {
  final AgentConfig? initialConfig;
  const _ImageKeySection({
    required this.initialConfig,
  });
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final viewmodel =
        ref.read(agentConfigScreenViewModelProvider(initialConfig));
    final (imageKeys, selectImageKey) = ref.watch(
      agentConfigScreenViewModelProvider(initialConfig).select(
        (it) => (
          it.imageKeys,
          it.selectImageKey,
        ),
      ),
    );
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(t.agentConfig.agentImage),
        DropdownButton<String>(
          value: selectImageKey,
          onChanged: (String? newValue) => viewmodel.updateImageKey(newValue),
          items: imageKeys.map<DropdownMenuItem<String>>((String item) {
            return DropdownMenuItem<String>(
              value: item,
              child: Text(item),
            );
          }).toList(),
        ),
      ],
    );
  }
}
