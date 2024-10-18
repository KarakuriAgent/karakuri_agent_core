import 'package:flutter/widgets.dart';
import 'package:karakuri_agent/i18n/strings.g.dart';
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

  Future<void> initialize() async {
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

  void updateTextServiceConfig(ServiceConfig? config) {
    if (selectTextService != config) {
      selectTextModel = null;
    }
    selectTextService = config;
    textModels = config?.textConfig?.models ?? [];
    notifyListeners();
  }

  void updateSpeechToTextServiceConfig(ServiceConfig? config) {
    if (selectSpeechToTextService != config) {
      selectSpeechToTextModel = null;
    }
    selectSpeechToTextService = config;
    speechToTextModels = config?.speechToTextConfig?.models ?? [];
    notifyListeners();
  }

  void updateTextToSpeechServiceConfig(ServiceConfig? config) {
    if (selectTextToSpeechService != config) {
      selectTextToSpeechVoice = null;
    }
    selectTextToSpeechService = config;
    textToSpeechVoices = config?.textToSpeechConfig?.voices ?? [];
    notifyListeners();
  }

  void updateTextModel(KeyValuePair? model) {
    selectTextModel = model;
    notifyListeners();
  }

  void updateSpeechToTextModel(KeyValuePair? model) {
    selectSpeechToTextModel = model;
    notifyListeners();
  }

  void updateTextToSpeechVoice(KeyValuePair? voice) {
    selectTextToSpeechVoice = voice;
    notifyListeners();
  }

  String? validationCheck() {
    if (nameController.text.isEmpty) {
      return t.home.agent.error.nameIsRequired;
    }
    if (selectTextService == null) {
      return t.home.agent.error.textServiceRequired;
    }
    if (selectTextModel == null) {
      return t.home.agent.error.textModelRequired;
    }
    if (selectSpeechToTextService == null) {
      return t.home.agent.error.speechToTextServiceRequired;
    }
    if (selectSpeechToTextModel == null) {
      return t.home.agent.error.speechToTextModelRequired;
    }
    if (selectTextToSpeechService == null) {
      return t.home.agent.error.textToSpeechServiceRequired;
    }
    if (selectTextToSpeechVoice == null) {
      return t.home.agent.error.textToSpeechVoiceRequired;
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
