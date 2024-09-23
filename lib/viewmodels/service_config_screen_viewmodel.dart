import 'package:flutter/widgets.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/models/stt_config.dart';
import 'package:karakuri_agent/models/text_config.dart';
import 'package:karakuri_agent/models/tts_config.dart';
import 'package:karakuri_agent/i18n/strings.g.dart';

class ServiceConfigScreenViewmodel {
  final Ref _ref;
  final String? _id;
  final AutoDisposeStateProvider<TextEditingController> nameControllerProvider;
  final AutoDisposeStateProvider<TextEditingController>
      baseUrlControllerProvider;
  final AutoDisposeStateProvider<TextEditingController>
      apiKeyControllerProvider;
  final AutoDisposeStateProvider<ServiceType> serviceTypeProvider;
  final AutoDisposeStateProvider<List<TextEditPair>> textConfigModelsProvider;
  final AutoDisposeStateProvider<List<TextEditPair>> sttConfigModelsProvider;
  final AutoDisposeStateProvider<List<TextEditPair>> ttsConfigVoicesProvider;

  ServiceConfigScreenViewmodel(this._ref, {ServiceConfig? serviceConfig})
      : _id = serviceConfig?.id,
        nameControllerProvider =
            StateProvider.autoDispose<TextEditingController>((ref) {
          final controller =
              TextEditingController(text: serviceConfig?.name ?? '');
          ref.onDispose(() {
            controller.dispose();
          });
          return controller;
        }),
        baseUrlControllerProvider =
            StateProvider.autoDispose<TextEditingController>((ref) {
          final controller =
              TextEditingController(text: serviceConfig?.baseUrl ?? '');
          ref.onDispose(() {
            
            controller.dispose();
          });
          return controller;
        }),
        apiKeyControllerProvider =
            StateProvider.autoDispose<TextEditingController>((ref) {
          final controller =
              TextEditingController(text: serviceConfig?.apiKey ?? '');
          ref.onDispose(() {
            controller.dispose();
          });
          return controller;
        }),
        serviceTypeProvider = StateProvider.autoDispose<ServiceType>(
            (ref) => serviceConfig?.type ?? ServiceType.openAI),
        textConfigModelsProvider =
            StateProvider.autoDispose<List<TextEditPair>>((ref) =>
                TextEditPair.fromList(serviceConfig?.textConfig?.models)),
        sttConfigModelsProvider = StateProvider.autoDispose<List<TextEditPair>>(
            (ref) => TextEditPair.fromList(serviceConfig?.sttConfig?.models)),
        ttsConfigVoicesProvider = StateProvider.autoDispose<List<TextEditPair>>(
            (ref) => TextEditPair.fromList(serviceConfig?.ttsConfig?.voices)) {
  
    _ref.onDispose(() {
      _disposeList(_ref.read(textConfigModelsProvider));
      _disposeList(_ref.read(sttConfigModelsProvider));
      _disposeList(_ref.read(ttsConfigVoicesProvider));
    });
  }

  void _disposeList(List<TextEditPair> list) {
    for (var pair in list) {
      pair.dispose();
    }
  }

  void updateServiceType(ServiceType type) {
    _ref.read(serviceTypeProvider.notifier).state = type;
  }

  void addTextConfigModels() {
    _ref.read(textConfigModelsProvider.notifier).update((state) {
      state.add(TextEditPair());
      return List.from(state);
    });
  }

  void addSTTConfigModels() {
    _ref.read(sttConfigModelsProvider.notifier).update((state) {
      state.add(TextEditPair());
      return List.from(state);
    });
  }

  void addTTSConfigVoices() {
    _ref.read(ttsConfigVoicesProvider.notifier).update((state) {
      state.add(TextEditPair());
      return List.from(state);
    });
  }

  void clearTextConfigModels() {
    _ref.read(textConfigModelsProvider.notifier).update((state) {
      _disposeList(state);
      state.clear();
      return [];
    });
  }

  void clearSTTConfigModels() {
    _ref.read(sttConfigModelsProvider.notifier).update((state) {
      _disposeList(state);
      state.clear();
      return [];
    });
  }

  void clearTTSConfigVoices() {
    _ref.read(ttsConfigVoicesProvider.notifier).update((state) {
      _disposeList(state);
      state.clear();
      return [];
    });
  }

  void removeTextConfigModelsAt(int index) {
    _ref.read(textConfigModelsProvider.notifier).update((state) {
      state[index].dispose();
      state.removeAt(index);
      return List.from(state);
    });
  }

  void removeSTTConfigModelsAt(int index) {
    _ref.read(sttConfigModelsProvider.notifier).update((state) {
      state[index].dispose();
      state.removeAt(index);
      return List.from(state);
    });
  }

  void removeTTSConfigVoicesAt(int index) {
    _ref.read(ttsConfigVoicesProvider.notifier).update((state) {
      state[index].dispose();
      state.removeAt(index);
      return List.from(state);
    });
  }

  String? validationCheck() {
    final name = _ref.read(nameControllerProvider).text;
    if (name.isEmpty) {
      return t.settings.serviceSettings.serviceConfig.error.nameIsRequired;
    }

    final baseUrl = _ref.read(baseUrlControllerProvider).text;
    if (baseUrl.isEmpty) {
      return t.settings.serviceSettings.serviceConfig.error.baseUrlIsRequired;
    }

    final apiKey = _ref.read(apiKeyControllerProvider).text;
    if (apiKey.isEmpty) {
      return t.settings.serviceSettings.serviceConfig.error.apiKeyIsRequired;
    }

    final type = _ref.read(serviceTypeProvider);
    if (type.capabilities.supportsText) {
      final textConfigModels = _ref.read(textConfigModelsProvider);
      if (textConfigModels.isNotEmpty) {
        final Set<String> keys = {};
        for (var model in textConfigModels) {
          if (model.keyController.value.text.isEmpty) {
            return t.settings.serviceSettings.serviceConfig.error
                .textModelKeyIsRequired;
          }
          if (model.valueController.value.text.isEmpty) {
            return t.settings.serviceSettings.serviceConfig.error
                .textModelValueIsRequired;
          }
          if (!keys.add(model.keyController.value.text)) {
            return t.settings.serviceSettings.serviceConfig.error
                .duplicateTextModelkey(key: model.keyController.value.text);
          }
        }
      }
    }

    if (type.capabilities.supportsSpeechToText) {
      final sttConfigModels = _ref.read(sttConfigModelsProvider);
      if (sttConfigModels.isNotEmpty) {
        final Set<String> keys = {};
        for (var model in sttConfigModels) {
          if (model.keyController.value.text.isEmpty) {
            return t.settings.serviceSettings.serviceConfig.error
                .sttModelKeyIsRequired;
          }
          if (model.valueController.value.text.isEmpty) {
            return t.settings.serviceSettings.serviceConfig.error
                .sttModelValueIsRequired;
          }
          if (!keys.add(model.keyController.value.text)) {
            return t.settings.serviceSettings.serviceConfig.error
                .duplicateSttModelkey(key: model.keyController.value.text);
          }
        }
      }
    }

    if (type.capabilities.supportsTextToSpeech) {
      final ttsConfigVoices = _ref.read(ttsConfigVoicesProvider);
      if (ttsConfigVoices.isNotEmpty) {
        final Set<String> keys = {};
        for (var voice in ttsConfigVoices) {
          if (voice.keyController.value.text.isEmpty) {
            return t.settings.serviceSettings.serviceConfig.error
                .ttsVoiceKeyIsRequired;
          }
          if (voice.valueController.value.text.isEmpty) {
            return t.settings.serviceSettings.serviceConfig.error
                .ttsVoiceValueIsRequired;
          }
          if (!keys.add(voice.keyController.value.text)) {
            return t.settings.serviceSettings.serviceConfig.error
                .duplicateTtsVoicekey(key: voice.keyController.value.text);
          }
        }
      }
    }
    return null;
  }

  ServiceConfig createServiceConfig() {
    return ServiceConfig(
      id: _id,
      name: _ref.read(nameControllerProvider).text,
      type: _ref.read(serviceTypeProvider),
      baseUrl: _ref.read(baseUrlControllerProvider).text,
      apiKey: _ref.read(apiKeyControllerProvider).text,
      textConfig: _createTextConfig(_ref.read(textConfigModelsProvider)),
      ttsConfig: _createTTSConfig(_ref.read(ttsConfigVoicesProvider)),
      sttConfig: _createSTTConfig(_ref.read(sttConfigModelsProvider)),
    );
  }

  TextConfig? _createTextConfig(List<TextEditPair> models) {
    if (models.isEmpty) {
      return null;
    } else {
      final newModels = models
          .map((model) => {
                model.keyController.value.text: model.valueController.value.text
              })
          .toList();
      return TextConfig(models: newModels);
    }
  }

  STTConfig? _createSTTConfig(List<TextEditPair> models) {
    if (models.isEmpty) {
      return null;
    } else {
      final newModels = models
          .map((model) => {
                model.keyController.value.text: model.valueController.value.text
              })
          .toList();
      return STTConfig(models: newModels);
    }
  }

  TTSConfig? _createTTSConfig(List<TextEditPair> voices) {
    if (voices.isEmpty) {
      return null;
    } else {
      final newVoices = voices
          .map((voice) => {
                voice.keyController.value.text: voice.valueController.value.text
              })
          .toList();
      return TTSConfig(voices: newVoices);
    }
  }
}

class TextEditPair {
  final TextEditingController keyController;
  final TextEditingController valueController;

  TextEditPair({String key = '', String value = ''})
      : keyController = TextEditingController(text: key),
        valueController = TextEditingController(text: value);

  void dispose() {
    keyController.dispose();
    valueController.dispose();
  }

  static List<TextEditPair> fromList(List<Map<String, String>>? list) {
    if (list == null || list.isEmpty) {
      return [];
    }
    return list.map((map) {
      final entry = map.entries.first;
      return TextEditPair(key: entry.key, value: entry.value);
    }).toList();
  }
}
