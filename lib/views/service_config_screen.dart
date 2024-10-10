import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/config_type.dart';
import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/providers/service_config_screen_viewmodel_provider.dart';
import 'package:karakuri_agent/viewmodels/service_config_screen_viewmodel.dart';
import 'package:karakuri_agent/i18n/strings.g.dart';

class ServiceConfigScreen extends HookConsumerWidget {
  final ServiceConfig? initialConfig;

  const ServiceConfigScreen({super.key, this.initialConfig});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final viewModel =
        ref.watch(serviceConfigScreenViewmodelProvider(initialConfig));
    final selectedType = ref.watch(viewModel.serviceTypeProvider);

    // TODO サポート対象外になった場合、watchしなくなるためデフォルト値に戻ってします。
    ref.watch(viewModel.textConfigModelsProvider);
    ref.watch(viewModel.speechToTextConfigModelsProvider);
    ref.watch(viewModel.textToSpeechConfigVoicesProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(initialConfig == null
            ? t.settings.serviceSettings.serviceConfig.serviceAdd
            : t.settings.serviceSettings.serviceConfig.serviceEdit),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _BaseConfigSection(viewModel: viewModel),
            _ServiceTypeDropdownSection(viewModel: viewModel),
            if (selectedType.capabilities.supportsText)
              Padding(
                padding: const EdgeInsets.only(
                  bottom: 3,
                ),
                child: _TextConfigSection(viewModel: viewModel),
              ),
            if (selectedType.capabilities.supportsSpeechToText)
              Padding(
                padding: const EdgeInsets.only(
                  bottom: 3,
                ),
                child: _SpeechToTextConfigSection(viewModel: viewModel),
              ),
            if (selectedType.capabilities.supportsTextToSpeech)
              Padding(
                padding: const EdgeInsets.only(
                  bottom: 3,
                ),
                child: _TextToSpeechConfigSection(viewModel: viewModel),
              ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () => _saveConfig(context, ref, viewModel),
              child: Text(t.settings.serviceSettings.serviceConfig.save),
            ),
          ],
        ),
      ),
    );
  }

  void _saveConfig(
    BuildContext context,
    WidgetRef ref,
    ServiceConfigScreenViewmodel viewModel,
  ) {
    final error = viewModel.validationCheck();
    if (error != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(error),
      ));
      return;
    }
    Navigator.of(context).pop(viewModel.createServiceConfig());
  }
}

class _BaseConfigSection extends HookConsumerWidget {
  final ServiceConfigScreenViewmodel viewModel;

  const _BaseConfigSection({required this.viewModel});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final nameController = ref.watch(viewModel.nameControllerProvider);
    final baseUrlController = ref.watch(viewModel.baseUrlControllerProvider);
    final apiKeyController = ref.watch(viewModel.apiKeyControllerProvider);
    return Column(
      children: [
        TextFormField(
          controller: nameController,
          decoration: InputDecoration(
              labelText: t.settings.serviceSettings.serviceConfig.name),
        ),
        TextFormField(
          controller: baseUrlController,
          decoration: InputDecoration(
              labelText: t.settings.serviceSettings.serviceConfig.baseUrl),
        ),
        TextFormField(
          controller: apiKeyController,
          decoration: InputDecoration(
              labelText: t.settings.serviceSettings.serviceConfig.apiKey),
        ),
      ],
    );
  }
}

class _ServiceTypeDropdownSection extends HookConsumerWidget {
  final ServiceConfigScreenViewmodel viewModel;

  const _ServiceTypeDropdownSection({
    required this.viewModel,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedType = ref.watch(viewModel.serviceTypeProvider);
    return DropdownButtonFormField<ServiceType>(
      value: selectedType,
      onChanged: (ServiceType? newValue) {
        if (newValue != null) {
          if (!newValue.capabilities.supportsText) {
            viewModel.clearTextConfigModels();
          }
          if (!newValue.capabilities.supportsSpeechToText) {
            viewModel.clearSpeechToTextConfigModels();
          }
          if (!newValue.capabilities.supportsTextToSpeech) {
            viewModel.clearTextToSpeechConfigVoices();
          }
          viewModel.updateServiceType(newValue);
        }
      },
      items: ServiceType.values.map((ServiceType type) {
        return DropdownMenuItem<ServiceType>(
          value: type,
          child: Text(type.displayName),
        );
      }).toList(),
      decoration: InputDecoration(
          labelText: t.settings.serviceSettings.serviceConfig.serviceType),
    );
  }
}

class _ToggleConfigSection extends StatelessWidget {
  final ServiceConfigScreenViewmodel viewModel;
  final ConfigType configType;
  final bool selectedConfigSection;

  const _ToggleConfigSection({
    required this.viewModel,
    required this.configType,
    required this.selectedConfigSection,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: () {
        if (selectedConfigSection) {
          if (configType == ConfigType.text) {
            viewModel.clearTextConfigModels();
          } else if (configType == ConfigType.stt) {
            viewModel.clearSpeechToTextConfigModels();
          } else if (configType == ConfigType.tts) {
            viewModel.clearTextToSpeechConfigVoices();
          }
        } else {
          if (configType == ConfigType.text) {
            viewModel.addTextConfigModels();
          } else if (configType == ConfigType.stt) {
            viewModel.addSpeechToTextConfigModels();
          } else if (configType == ConfigType.tts) {
            viewModel.addTextToSpeechConfigVoices();
          }
        }
      },
      child: Text(
        selectedConfigSection
            ? t.settings.serviceSettings.serviceConfig
                .configDelete(configType: configType.name)
            : t.settings.serviceSettings.serviceConfig
                .configAdd(configType: configType.name),
      ),
    );
  }
}

class _ConfigSectionBase extends HookConsumerWidget {
  final ServiceConfigScreenViewmodel viewModel;
  final ConfigType configType;
  final bool selectedConfigSection;

  const _ConfigSectionBase({
    required this.viewModel,
    required this.configType,
    required this.selectedConfigSection,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _ToggleConfigSection(
            viewModel: viewModel,
            configType: configType,
            selectedConfigSection: selectedConfigSection),
        if (selectedConfigSection) ...[
          const SizedBox(height: 16),
          Text(configType.title),
        ],
      ],
    );
  }
}

class _ConfigSectionMap extends HookConsumerWidget {
  final String title;
  final String labelKey;
  final String labelValue;
  final String labelAdd;

  final List<TextEditPair> map;
  final VoidCallback onAdd;
  final VoidCallback onRemove;

  const _ConfigSectionMap({
    required this.title,
    required this.labelKey,
    required this.labelValue,
    required this.labelAdd,
    required this.map,
    required this.onAdd,
    required this.onRemove,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title),
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: map.length,
          itemBuilder: (context, index) {
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 4.0),
              child: Row(
                children: [
                  Expanded(
                    flex: 4,
                    child: TextFormField(
                      controller: map[index].keyController,
                      decoration: InputDecoration(labelText: labelKey),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    flex: 4,
                    child: TextFormField(
                      controller: map[index].valueController,
                      decoration: InputDecoration(labelText: labelValue),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    icon: const Icon(Icons.remove_circle),
                    onPressed: onRemove,
                  ),
                ],
              ),
            );
          },
        ),
        const SizedBox(height: 8),
        ElevatedButton.icon(
          onPressed: onAdd,
          icon: const Icon(Icons.add),
          label: Text(labelAdd),
        ),
      ],
    );
  }
}

class _TextConfigSection extends HookConsumerWidget {
  final ServiceConfigScreenViewmodel viewModel;

  const _TextConfigSection({
    required this.viewModel,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final models = ref.watch(viewModel.textConfigModelsProvider);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _ConfigSectionBase(
          viewModel: viewModel,
          configType: ConfigType.text,
          selectedConfigSection: models.isNotEmpty,
        ),
        if (models.isNotEmpty)
          _ConfigSectionMap(
            title: t.settings.serviceSettings.serviceConfig.textConfig.models,
            labelKey: t.settings.serviceSettings.serviceConfig.textConfig.id,
            labelValue:
                t.settings.serviceSettings.serviceConfig.textConfig.name,
            labelAdd:
                t.settings.serviceSettings.serviceConfig.textConfig.addModel,
            map: models,
            onAdd: viewModel.addTextConfigModels,
            onRemove: () {
              if (models.length > 1) {
                viewModel.removeTextConfigModelsAt(0);
              }
            },
          ),
      ],
    );
  }
}

class _SpeechToTextConfigSection extends HookConsumerWidget {
  final ServiceConfigScreenViewmodel viewModel;

  const _SpeechToTextConfigSection({
    required this.viewModel,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final models = ref.watch(viewModel.speechToTextConfigModelsProvider);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _ConfigSectionBase(
          viewModel: viewModel,
          configType: ConfigType.stt,
          selectedConfigSection: models.isNotEmpty,
        ),
        if (models.isNotEmpty)
          _ConfigSectionMap(
            title: t.settings.serviceSettings.serviceConfig.speechToTextConfig.models,
            labelKey: t.settings.serviceSettings.serviceConfig.speechToTextConfig.id,
            labelValue: t.settings.serviceSettings.serviceConfig.speechToTextConfig.name,
            labelAdd:
                t.settings.serviceSettings.serviceConfig.speechToTextConfig.addModel,
            map: models,
            onAdd: viewModel.addSpeechToTextConfigModels,
            onRemove: () {
              if (models.length > 1) {
                viewModel.removeSpeechToTextConfigModelsAt(0);
              }
            },
          ),
      ],
    );
  }
}

class _TextToSpeechConfigSection extends HookConsumerWidget {
  final ServiceConfigScreenViewmodel viewModel;

  const _TextToSpeechConfigSection({
    required this.viewModel,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final voices = ref.watch(viewModel.textToSpeechConfigVoicesProvider);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _ConfigSectionBase(
          viewModel: viewModel,
          configType: ConfigType.tts,
          selectedConfigSection: voices.isNotEmpty,
        ),
        if (voices.isNotEmpty)
          _ConfigSectionMap(
            title: t.settings.serviceSettings.serviceConfig.textToSpeechConfig.voices,
            labelKey: t.settings.serviceSettings.serviceConfig.textToSpeechConfig.id,
            labelValue: t.settings.serviceSettings.serviceConfig.textToSpeechConfig.name,
            labelAdd:
                t.settings.serviceSettings.serviceConfig.textToSpeechConfig.addVoice,
            map: voices,
            onAdd: viewModel.addTextToSpeechConfigVoices,
            onRemove: () {
              if (voices.length > 1) {
                viewModel.removeTextToSpeechConfigVoicesAt(0);
              }
            },
          ),
      ],
    );
  }
}
