import 'package:flutter/widgets.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/key_value_pair.dart';
import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/repositories/config_storage_repository.dart';

class AgentConfigScreenViewmodel extends ChangeNotifier {
  final ConfigStorageRepository _configStorage;
  final int? _id;
  final TextEditingController nameController;
  final List<ServiceConfig> textServiceConfigs = [];
  List<KeyValuePair> textModels;
  final List<ServiceConfig> speechToTextServiceConfigs = [];
  List<KeyValuePair> speechToTextModels;
  final List<ServiceConfig> textToSpeechServiceConfigs = [];
  List<KeyValuePair> textToSpeechVoices;

  bool initialized = false;
  ServiceConfig? selectTextService;
  KeyValuePair? selectTextModel;
  ServiceConfig? selectSpeechToTextService;
  KeyValuePair? selectSpeechToTextModel;
  ServiceConfig? selectTextToSpeechService;
  KeyValuePair? selectTextToSpeechVoice;
  AgentConfigScreenViewmodel(this._configStorage, {AgentConfig? agentConfig})
      : _id = agentConfig?.id,
        nameController = TextEditingController(text: agentConfig?.name ?? ''),
        selectTextService = agentConfig?.textServiceConfig,
        textModels = agentConfig?.textServiceConfig.textConfig?.models ?? [],
        selectTextModel = agentConfig?.textModel,
        selectSpeechToTextService = agentConfig?.speechToTextServiceConfig,
        speechToTextModels =
            agentConfig?.speechToTextServiceConfig.speechToTextConfig?.models ??
                [],
        selectSpeechToTextModel = agentConfig?.speechToTextModel,
        selectTextToSpeechService = agentConfig?.textToSpeechServiceConfig,
        textToSpeechVoices =
            agentConfig?.textToSpeechServiceConfig.textToSpeechConfig?.voices ??
                [],
        selectTextToSpeechVoice = agentConfig?.textToSpeechVoice;

  Future<void> build() async {
    textServiceConfigs.addAll(await _configStorage.loadTextServiceConfigs());
    speechToTextServiceConfigs
        .addAll(await _configStorage.loadSpeechToTextServiceConfigs());
    textToSpeechServiceConfigs
        .addAll(await _configStorage.loadTextToSpeechServiceConfigs());
    initialized = true;
    notifyListeners();
  }

  @override
  void dispose() {
    nameController.dispose();
    super.dispose();
  }

  void setTextServiceConfig(ServiceConfig? config) {
    if (selectTextService != config) {
      selectTextModel = null;
    }
    selectTextService = config;
    textModels = config?.textConfig?.models ?? [];
    notifyListeners();
  }

  void setSpeechToTextServiceConfig(ServiceConfig? config) {
    if (selectSpeechToTextService != config) {
      selectSpeechToTextModel = null;
    }
    selectSpeechToTextService = config;
    speechToTextModels = config?.speechToTextConfig?.models ?? [];
    notifyListeners();
  }

  void setTextToSpeechServiceConfig(ServiceConfig? config) {
    if (selectTextToSpeechService != config) {
      selectTextToSpeechVoice = null;
    }
    selectTextToSpeechService = config;
    textToSpeechVoices = config?.textToSpeechConfig?.voices ?? [];
    notifyListeners();
  }

  void setTextModel(KeyValuePair? model) {
    selectTextModel = model;
    notifyListeners();
  }

  void setSpeechToText(KeyValuePair? model) {
    selectSpeechToTextModel = model;
    notifyListeners();
  }

  void setTextToSpeech(KeyValuePair? voice) {
    selectTextToSpeechVoice = voice;
    notifyListeners(); 
  }

  String? validationCheck() {
    // TODO
    if (nameController.text.isEmpty) {
      // return t.settings.serviceSettings.serviceConfig.error.nameIsRequired;
    }
    if (selectTextService == null) {
      // return t.settings.serviceSettings.serviceConfig.error.textServiceIsRequired;
    }
    if (selectTextModel == null) {
      // return t.settings.serviceSettings.serviceConfig.error.textModelIsRequired;
    }
    if (selectSpeechToTextService == null) {
      // return t.settings.serviceSettings.serviceConfig.error.speechToTextServiceIsRequired;
    }
    return null;
  }

  AgentConfig createAgentConfig() {
    return AgentConfig(
      id: _id,
      name: nameController.text,
      textServiceConfig: selectTextService!,
      textModel: selectTextModel!,
      speechToTextServiceConfig: selectSpeechToTextService!,
      speechToTextModel: selectSpeechToTextModel!,
      textToSpeechServiceConfig: selectTextToSpeechService!,
      textToSpeechVoice: selectTextToSpeechVoice!,
    );
  }
}
