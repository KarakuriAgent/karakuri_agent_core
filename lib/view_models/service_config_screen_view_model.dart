import 'package:flutter/widgets.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/i18n/strings.g.dart';
import 'package:karakuri_agent/models/key_value_pair.dart';
import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/models/speech_to_text_config.dart';
import 'package:karakuri_agent/models/text_config.dart';
import 'package:karakuri_agent/models/text_to_speech_config.dart';
import 'package:karakuri_agent/providers/default_param_provider.dart';

class ServiceConfigScreenViewModel extends ChangeNotifier {
  final Ref _ref;
  final int? _id;
  final TextEditingController nameController;
  final TextEditingController baseUrlController;
  final TextEditingController apiKeyController;
  ServiceType _serviceType;
  List<TextEditPair> _textConfigModels;
  List<TextEditPair> _speechToTextConfigModels;
  List<TextEditPair> _textToSpeechConfigModels;
  List<TextEditPair> _textToSpeechConfigVoices;

  ServiceType get serviceType => _serviceType;
  List<TextEditPair> get textConfigModels => _textConfigModels;
  List<TextEditPair> get speechToTextConfigModels => _speechToTextConfigModels;
  List<TextEditPair> get textToSpeechConfigModels => _textToSpeechConfigModels;
  List<TextEditPair> get textToSpeechConfigVoices => _textToSpeechConfigVoices;

  ServiceConfigScreenViewModel(this._ref, {ServiceConfig? serviceConfig})
      : _id = serviceConfig?.id,
        nameController = TextEditingController(text: serviceConfig?.name ?? ''),
        baseUrlController =
            TextEditingController(text: serviceConfig?.baseUrl ?? ''),
        apiKeyController =
            TextEditingController(text: serviceConfig?.apiKey ?? ''),
        _serviceType = serviceConfig?.type ?? ServiceType.openAI,
        _textConfigModels =
            TextEditPair.fromList(serviceConfig?.textConfig?.models),
        _speechToTextConfigModels =
            TextEditPair.fromList(serviceConfig?.speechToTextConfig?.models),
        _textToSpeechConfigModels =
            TextEditPair.fromList(serviceConfig?.textToSpeechConfig?.models),
        _textToSpeechConfigVoices =
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
    _serviceType = type;
    notifyListeners();
  }

  void createTextConfigModels() {
    _textConfigModels = _ref
        .read(defaultParamProvider(serviceType))
        .textmodels
        .map((v) => TextEditPair(key: v.key, value: v.value))
        .toList();
    notifyListeners();
  }

  void addTextConfigModels() {
    _textConfigModels = [...textConfigModels, TextEditPair()];
    notifyListeners();
  }

  void createSpeechToTextConfigModels() {
    _speechToTextConfigModels = _ref
        .read(defaultParamProvider(serviceType))
        .speechToTextModels
        .map((v) => TextEditPair(key: v.key, value: v.value))
        .toList();
    notifyListeners();
  }

  void addSpeechToTextConfigModels() {
    _speechToTextConfigModels = [...speechToTextConfigModels, TextEditPair()];
    notifyListeners();
  }

  void createTextToSpeechConfigModels() {
    _textToSpeechConfigModels = _ref
        .read(defaultParamProvider(serviceType))
        .textToSpeechModels
        .map((v) => TextEditPair(key: v.key, value: v.value))
        .toList();
    notifyListeners();
  }

  void addTextToSpeechConfigModels() {
    _textToSpeechConfigModels = [...textToSpeechConfigModels, TextEditPair()];
    notifyListeners();
  }

  void createTextToSpeechConfigVoices() {
    _textToSpeechConfigVoices = _ref
        .read(defaultParamProvider(serviceType))
        .textToSpeechVoices
        .map((v) => TextEditPair(key: v.key, value: v.value))
        .toList();
    notifyListeners();
  }

  void addTextToSpeechConfigVoices() {
    _textToSpeechConfigVoices = [...textToSpeechConfigVoices, TextEditPair()];
    notifyListeners();
  }

  void clearTextConfigModels() => _clearTextEditPairs(
      () => textConfigModels, (models) => _textConfigModels = models);

  void clearSpeechToTextConfigModels() => _clearTextEditPairs(
      () => speechToTextConfigModels,
      (models) => _speechToTextConfigModels = models);

  void clearTextToSpeechConfigModels() => _clearTextEditPairs(
      () => textToSpeechConfigModels,
      (models) => _textToSpeechConfigModels = models);

  void clearTextToSpeechConfigVoices() => _clearTextEditPairs(
      () => textToSpeechConfigVoices,
      (voices) => _textToSpeechConfigVoices = voices);

  void removeTextConfigModelsAt(int index) => _removeTextEditPairAt(
      () => textConfigModels, (models) => _textConfigModels = models, index);

  void removeSpeechToTextConfigModelsAt(int index) => _removeTextEditPairAt(
      () => speechToTextConfigModels,
      (models) => _speechToTextConfigModels = models,
      index);

  void removeTextToSpeechConfigModelsAt(int index) => _removeTextEditPairAt(
      () => textToSpeechConfigModels,
      (models) => _textToSpeechConfigModels = models,
      index);

  void removeTextToSpeechConfigVoicesAt(int index) => _removeTextEditPairAt(
      () => textToSpeechConfigVoices,
      (voices) => _textToSpeechConfigVoices = voices,
      index);

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
      final newModels = _mapTextEditPairsToKeyValuePairs(models);
      return TextConfig(models: newModels);
    }
  }

  SpeechToTextConfig? _createSpeechToTextConfig(List<TextEditPair> models) {
    if (models.isEmpty) {
      return null;
    } else {
      final newModels = _mapTextEditPairsToKeyValuePairs(models);
      return SpeechToTextConfig(models: newModels);
    }
  }

  TextToSpeechConfig? _createTextToSpeechConfig(
      List<TextEditPair> models, List<TextEditPair> voices) {
    if (models.isEmpty || voices.isEmpty) {
      return null;
    } else {
      final newModels = _mapTextEditPairsToKeyValuePairs(models);
      final newVoices = _mapTextEditPairsToKeyValuePairs(voices);
      return TextToSpeechConfig(models: newModels, voices: newVoices);
    }
  }

  List<KeyValuePair> _mapTextEditPairsToKeyValuePairs(
      List<TextEditPair> pairs) {
    return pairs
        .map((pair) => KeyValuePair(
            key: pair.keyController.value.text,
            value: pair.valueController.value.text))
        .toList();
  }

  void _clearTextEditPairs<T>(
      List<T> Function() getter, void Function(List<T>) setter) {
    setter([]);
    notifyListeners();
  }

  void _removeTextEditPairAt<T>(
      List<T> Function() getter, void Function(List<T>) setter, int index) {
    setter(List.from(getter())..removeAt(index));
    notifyListeners();
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
