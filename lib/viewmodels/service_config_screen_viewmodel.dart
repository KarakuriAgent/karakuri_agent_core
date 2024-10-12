import 'package:flutter/widgets.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/key_value_pair.dart';
import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/models/speech_to_text_config.dart';
import 'package:karakuri_agent/models/text_config.dart';
import 'package:karakuri_agent/models/text_to_speech_config.dart';
import 'package:karakuri_agent/i18n/strings.g.dart';

class ServiceConfigScreenViewmodel {
  final Ref _ref;
  final int? _id;
  final AutoDisposeStateProvider<TextEditingController> nameControllerProvider;
  final AutoDisposeStateProvider<TextEditingController>
      baseUrlControllerProvider;
  final AutoDisposeStateProvider<TextEditingController>
      apiKeyControllerProvider;
  final AutoDisposeStateProvider<ServiceType> serviceTypeProvider;
  final AutoDisposeStateProvider<List<TextEditPair>> textConfigModelsProvider;
  final AutoDisposeStateProvider<List<TextEditPair>>
      speechToTextConfigModelsProvider;
  final AutoDisposeStateProvider<List<TextEditPair>>
      textToSpeechConfigVoicesProvider;

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
        speechToTextConfigModelsProvider =
            StateProvider.autoDispose<List<TextEditPair>>((ref) =>
                TextEditPair.fromList(
                    serviceConfig?.speechToTextConfig?.models)),
        textToSpeechConfigVoicesProvider =
            StateProvider.autoDispose<List<TextEditPair>>((ref) =>
                TextEditPair.fromList(
                    serviceConfig?.textToSpeechConfig?.voices)) {
    _ref.onDispose(() {
      _disposeList(_ref.read(textConfigModelsProvider));
      _disposeList(_ref.read(speechToTextConfigModelsProvider));
      _disposeList(_ref.read(textToSpeechConfigVoicesProvider));
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

  void addSpeechToTextConfigModels() {
    _ref.read(speechToTextConfigModelsProvider.notifier).update((state) {
      state.add(TextEditPair());
      return List.from(state);
    });
  }

  void addTextToSpeechConfigVoices() {
    _ref.read(textToSpeechConfigVoicesProvider.notifier).update((state) {
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

  void clearSpeechToTextConfigModels() {
    _ref.read(speechToTextConfigModelsProvider.notifier).update((state) {
      _disposeList(state);
      state.clear();
      return [];
    });
  }

  void clearTextToSpeechConfigVoices() {
    _ref.read(textToSpeechConfigVoicesProvider.notifier).update((state) {
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

  void removeSpeechToTextConfigModelsAt(int index) {
    _ref.read(speechToTextConfigModelsProvider.notifier).update((state) {
      state[index].dispose();
      state.removeAt(index);
      return List.from(state);
    });
  }

  void removeTextToSpeechConfigVoicesAt(int index) {
    _ref.read(textToSpeechConfigVoicesProvider.notifier).update((state) {
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
      final speechToTextConfigModels =
          _ref.read(speechToTextConfigModelsProvider);
      if (speechToTextConfigModels.isNotEmpty) {
        final Set<String> keys = {};
        for (var model in speechToTextConfigModels) {
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
      final textToSpeechConfigVoices =
          _ref.read(textToSpeechConfigVoicesProvider);
      if (textToSpeechConfigVoices.isNotEmpty) {
        final Set<String> keys = {};
        for (var voice in textToSpeechConfigVoices) {
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
      textToSpeechConfig: _createTextToSpeechConfig(
          _ref.read(textToSpeechConfigVoicesProvider)),
      speechToTextConfig: _createSpeechToTextConfig(
          _ref.read(speechToTextConfigModelsProvider)),
    );
  }

  TextConfig? _createTextConfig(List<TextEditPair> models) {
    if (models.isEmpty) {
      return null;
    } else {
      final newModels = models
          .map((model) => KeyValuePair(
              key: model.keyController.value.text,
              value: model.valueController.value.text))
          .toList();
      return TextConfig(models: newModels);
    }
  }

  SpeechToTextConfig? _createSpeechToTextConfig(List<TextEditPair> models) {
    if (models.isEmpty) {
      return null;
    } else {
      final newModels = models
          .map((model) => KeyValuePair(
              key: model.keyController.value.text,
              value: model.valueController.value.text))
          .toList();
      return SpeechToTextConfig(models: newModels);
    }
  }

  TextToSpeechConfig? _createTextToSpeechConfig(List<TextEditPair> voices) {
    if (voices.isEmpty) {
      return null;
    } else {
      final newVoices = voices
          .map((model) => KeyValuePair(
              key: model.keyController.value.text,
              value: model.valueController.value.text))
          .toList();
      return TextToSpeechConfig(voices: newVoices);
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

  static List<TextEditPair> fromList(List<KeyValuePair>? list) {
    if (list == null || list.isEmpty) {
      return [];
    }
    return list.map((map) {
      return TextEditPair(key: map.key, value: map.value);
    }).toList();
  }
}
