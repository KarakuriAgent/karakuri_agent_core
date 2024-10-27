import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/config_type.dart';
import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/providers/view_model_providers.dart';
import 'package:karakuri_agent/view_models/service_config_screen_view_model.dart';
import 'package:karakuri_agent/i18n/strings.g.dart';

class ServiceConfigScreen extends HookConsumerWidget {
  final ServiceConfig? initialConfig;

  const ServiceConfigScreen({super.key, this.initialConfig});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.listen<ServiceConfigScreenViewModel>(
      serviceConfigScreenViewModelProvider(initialConfig),
      (_, __) {},
    );
    final viewModel =
        ref.read(serviceConfigScreenViewModelProvider(initialConfig));
    final selectedType = ref.watch(
        serviceConfigScreenViewModelProvider(initialConfig)
            .select((it) => it.serviceType));
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
            _BaseConfigSection(initialConfig: initialConfig),
            _ServiceTypeDropdownSection(initialConfig: initialConfig),
            if (selectedType.capabilities.supportsText)
              Padding(
                padding: const EdgeInsets.only(
                  bottom: 3,
                ),
                child: _TextConfigSection(initialConfig: initialConfig),
              ),
            if (selectedType.capabilities.supportsSpeechToText)
              Padding(
                padding: const EdgeInsets.only(
                  bottom: 3,
                ),
                child: _SpeechToTextConfigSection(initialConfig: initialConfig),
              ),
            if (selectedType.capabilities.supportsTextToSpeech)
              Padding(
                padding: const EdgeInsets.only(
                  bottom: 3,
                ),
                child: _TextToSpeechConfigSection(initialConfig: initialConfig),
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
    ServiceConfigScreenViewModel viewModel,
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
  final ServiceConfig? initialConfig;

  const _BaseConfigSection({required this.initialConfig});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final viewModel =
        ref.read(serviceConfigScreenViewModelProvider(initialConfig));
    return Column(
      children: [
        TextFormField(
          controller: viewModel.nameController,
          decoration: InputDecoration(
              labelText: t.settings.serviceSettings.serviceConfig.name),
        ),
        TextFormField(
          controller: viewModel.baseUrlController,
          decoration: InputDecoration(
              labelText: t.settings.serviceSettings.serviceConfig.baseUrl),
        ),
        TextFormField(
          controller: viewModel.apiKeyController,
          decoration: InputDecoration(
              labelText: t.settings.serviceSettings.serviceConfig.apiKey),
        ),
      ],
    );
  }
}

class _ServiceTypeDropdownSection extends HookConsumerWidget {
  final ServiceConfig? initialConfig;

  const _ServiceTypeDropdownSection({
    required this.initialConfig,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final viewModel =
        ref.read(serviceConfigScreenViewModelProvider(initialConfig));
    final selectedType = ref.watch(
        serviceConfigScreenViewModelProvider(initialConfig)
            .select((it) => it.serviceType));
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
            viewModel.clearTextToSpeechConfigModels();
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
  final ServiceConfigScreenViewModel viewModel;
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
            viewModel.clearTextToSpeechConfigModels();
            viewModel.clearTextToSpeechConfigVoices();
          }
        } else {
          if (configType == ConfigType.text) {
            viewModel.createTextConfigModels();
          } else if (configType == ConfigType.stt) {
            viewModel.createSpeechToTextConfigModels();
          } else if (configType == ConfigType.tts) {
            viewModel.createTextToSpeechConfigModels();
            viewModel.createTextToSpeechConfigVoices();
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
  final ServiceConfigScreenViewModel viewModel;
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
  final Function(int index) onRemove;

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
                    onPressed: () => onRemove(index),
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
  final ServiceConfig? initialConfig;

  const _TextConfigSection({
    required this.initialConfig,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final viewModel =
        ref.read(serviceConfigScreenViewModelProvider(initialConfig));
    final models = ref.watch(serviceConfigScreenViewModelProvider(initialConfig)
        .select((it) => it.textConfigModels));
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
            onRemove: (index) {
              if (models.length > 1) {
                viewModel.removeTextConfigModelsAt(index);
              }
            },
          ),
      ],
    );
  }
}

class _SpeechToTextConfigSection extends HookConsumerWidget {
  final ServiceConfig? initialConfig;

  const _SpeechToTextConfigSection({
    required this.initialConfig,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final viewModel =
        ref.read(serviceConfigScreenViewModelProvider(initialConfig));
    final models = ref.watch(serviceConfigScreenViewModelProvider(initialConfig)
        .select((it) => it.speechToTextConfigModels));
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
            title: t.settings.serviceSettings.serviceConfig.speechToTextConfig
                .models,
            labelKey:
                t.settings.serviceSettings.serviceConfig.speechToTextConfig.id,
            labelValue: t
                .settings.serviceSettings.serviceConfig.speechToTextConfig.name,
            labelAdd: t.settings.serviceSettings.serviceConfig
                .speechToTextConfig.addModel,
            map: models,
            onAdd: viewModel.addSpeechToTextConfigModels,
            onRemove: (index) {
              if (models.length > 1) {
                viewModel.removeSpeechToTextConfigModelsAt(index);
              }
            },
          ),
      ],
    );
  }
}

class _TextToSpeechConfigSection extends HookConsumerWidget {
  final ServiceConfig? initialConfig;

  const _TextToSpeechConfigSection({
    required this.initialConfig,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final viewModel =
        ref.read(serviceConfigScreenViewModelProvider(initialConfig));
    final (voices, models) = ref.watch(
      serviceConfigScreenViewModelProvider(initialConfig).select(
        (it) => (it.textToSpeechConfigVoices, it.textToSpeechConfigModels),
      ),
    );
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _ConfigSectionBase(
          viewModel: viewModel,
          configType: ConfigType.tts,
          selectedConfigSection: models.isNotEmpty || voices.isNotEmpty,
        ),
        if (models.isNotEmpty)
          _ConfigSectionMap(
            title: t.settings.serviceSettings.serviceConfig.textToSpeechConfig
                .models,
            labelKey:
                t.settings.serviceSettings.serviceConfig.textToSpeechConfig.id,
            labelValue: t
                .settings.serviceSettings.serviceConfig.textToSpeechConfig.name,
            labelAdd: t.settings.serviceSettings.serviceConfig
                .textToSpeechConfig.addModel,
            map: models,
            onAdd: viewModel.addTextToSpeechConfigModels,
            onRemove: (index) {
              if (models.length > 1) {
                viewModel.removeTextToSpeechConfigModelsAt(index);
              }
            },
          ),
        if (voices.isNotEmpty)
          _ConfigSectionMap(
            title: t.settings.serviceSettings.serviceConfig.textToSpeechConfig
                .voices,
            labelKey:
                t.settings.serviceSettings.serviceConfig.textToSpeechConfig.id,
            labelValue: t
                .settings.serviceSettings.serviceConfig.textToSpeechConfig.name,
            labelAdd: t.settings.serviceSettings.serviceConfig
                .textToSpeechConfig.addVoice,
            map: voices,
            onAdd: viewModel.addTextToSpeechConfigVoices,
            onRemove: (index) {
              if (voices.length > 1) {
                viewModel.removeTextToSpeechConfigVoicesAt(index);
              }
            },
          ),
      ],
    );
  }
}
