import 'package:flutter/widgets.dart';
import 'package:karakuri_agent/models/key_value_pair.dart';
import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/models/speech_to_text_config.dart';
import 'package:karakuri_agent/models/text_config.dart';
import 'package:karakuri_agent/models/text_to_speech_config.dart';
import 'package:karakuri_agent/i18n/strings.g.dart';

class ServiceConfigScreenViewmodel extends ChangeNotifier {
  final int? _id;
  final TextEditingController nameController;
  final TextEditingController baseUrlController;
  final TextEditingController apiKeyController;
  ServiceType serviceType;
  List<TextEditPair> textConfigModels;
  List<TextEditPair> speechToTextConfigModels;
  List<TextEditPair> textToSpeechConfigModels;
  List<TextEditPair> textToSpeechConfigVoices;

  ServiceConfigScreenViewmodel({ServiceConfig? serviceConfig})
      : _id = serviceConfig?.id,
        nameController = TextEditingController(text: serviceConfig?.name ?? ''),
        baseUrlController =
            TextEditingController(text: serviceConfig?.baseUrl ?? ''),
        apiKeyController =
            TextEditingController(text: serviceConfig?.apiKey ?? ''),
        serviceType = serviceConfig?.type ?? ServiceType.openAI,
        textConfigModels =
            TextEditPair.fromList(serviceConfig?.textConfig?.models),
        speechToTextConfigModels =
            TextEditPair.fromList(serviceConfig?.speechToTextConfig?.models),
        textToSpeechConfigModels =
            TextEditPair.fromList(serviceConfig?.textToSpeechConfig?.models),
        textToSpeechConfigVoices =
            TextEditPair.fromList(serviceConfig?.textToSpeechConfig?.voices);

  @override
  void dispose() {
    nameController.dispose();
    baseUrlController.dispose();
    apiKeyController.dispose();
    _disposeList(textConfigModels);
    _disposeList(speechToTextConfigModels);
    _disposeList(textToSpeechConfigModels);
    _disposeList(textToSpeechConfigVoices);
    super.dispose();
  }

  void _disposeList(List<TextEditPair> list) {
    for (var pair in list) {
      pair.dispose();
    }
  }

  void updateServiceType(ServiceType type) {
    serviceType = type;
    notifyListeners();
  }

  void addTextConfigModels() {
    textConfigModels = [...textConfigModels, TextEditPair()];
    notifyListeners();
  }

  void addSpeechToTextConfigModels() {
    speechToTextConfigModels = [...speechToTextConfigModels, TextEditPair()];
    notifyListeners();
  }

  void addTextToSpeechConfigModels() {
    textToSpeechConfigModels = [...textToSpeechConfigModels, TextEditPair()];
    notifyListeners();
  }

  void addTextToSpeechConfigVoices() {
    textToSpeechConfigVoices = [...textToSpeechConfigVoices, TextEditPair()];
    notifyListeners();
  }

  void clearTextConfigModels() {
    textConfigModels = [];
    notifyListeners();
  }

  void clearSpeechToTextConfigModels() {
    speechToTextConfigModels = [];
    notifyListeners();
  }

  void clearTextToSpeechConfigModels() {
    textToSpeechConfigModels = [];
    notifyListeners();
  }

  void clearTextToSpeechConfigVoices() {
    textToSpeechConfigVoices = [];
    notifyListeners();
  }

  void removeTextConfigModelsAt(int index) {
    textConfigModels = List.from(textConfigModels)..removeAt(index);
    notifyListeners();
  }

  void removeSpeechToTextConfigModelsAt(int index) {
    speechToTextConfigModels = List.from(speechToTextConfigModels)
      ..removeAt(index);
    notifyListeners();
  }

  void removeTextToSpeechConfigModelsAt(int index) {
    textToSpeechConfigModels = List.from(textToSpeechConfigModels)
      ..removeAt(index);
    notifyListeners();
  }

  void removeTextToSpeechConfigVoicesAt(int index) {
    textToSpeechConfigVoices = List.from(textToSpeechConfigVoices)
      ..removeAt(index);
    notifyListeners();
  }

  String? validationCheck() {
    if (nameController.text.isEmpty) {
      return t.settings.serviceSettings.serviceConfig.error.nameIsRequired;
    }

    if (baseUrlController.text.isEmpty) {
      return t.settings.serviceSettings.serviceConfig.error.baseUrlIsRequired;
    }

    if (apiKeyController.text.isEmpty) {
      return t.settings.serviceSettings.serviceConfig.error.apiKeyIsRequired;
    }

    if (serviceType.capabilities.supportsText) {
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

    if (serviceType.capabilities.supportsSpeechToText) {
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

    if (serviceType.capabilities.supportsTextToSpeech) {
      if (textToSpeechConfigModels.isNotEmpty) {
        final Set<String> keys = {};
        for (var model in textToSpeechConfigModels) {
          if (model.keyController.value.text.isEmpty) {
            return t.settings.serviceSettings.serviceConfig.error
                .ttsModelKeyIsRequired;
          }
          if (model.valueController.value.text.isEmpty) {
            return t.settings.serviceSettings.serviceConfig.error
                .ttsModelValueIsRequired;
          }
          if (!keys.add(model.keyController.value.text)) {
            return t.settings.serviceSettings.serviceConfig.error
                .duplicateTtsModelkey(key: model.keyController.value.text);
          }
        }
      }

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
      name: nameController.text,
      type: serviceType,
      baseUrl: baseUrlController.text,
      apiKey: apiKeyController.text,
      textConfig: _createTextConfig(textConfigModels),
      textToSpeechConfig: _createTextToSpeechConfig(
          textToSpeechConfigModels, textToSpeechConfigVoices),
      speechToTextConfig: _createSpeechToTextConfig(speechToTextConfigModels),
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

  TextToSpeechConfig? _createTextToSpeechConfig(
      List<TextEditPair> models, List<TextEditPair> voices) {
    if (models.isEmpty || voices.isEmpty) {
      return null;
    } else {
      final newModels = models
          .map((model) => KeyValuePair(
              key: model.keyController.value.text,
              value: model.valueController.value.text))
          .toList();

      final newVoices = voices
          .map((model) => KeyValuePair(
              key: model.keyController.value.text,
              value: model.valueController.value.text))
          .toList();
      return TextToSpeechConfig(models: newModels, voices: newVoices);
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
