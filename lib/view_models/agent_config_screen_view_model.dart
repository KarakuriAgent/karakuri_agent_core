import 'package:flutter/widgets.dart';
import 'package:karakuri_agent/i18n/strings.g.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/key_value_pair.dart';
import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/repositories/config_storage_repository.dart';
import 'package:karakuri_agent/repositories/image_storage_repository.dart';
import 'package:karakuri_agent/utils/exception.dart';

class AgentConfigScreenViewModel extends ChangeNotifier {
  final ConfigStorageRepository _configStorage;
  final int? _id;
  final List<String> _imageKeys = [];
  final TextEditingController nameController;
  final List<ServiceConfig> textServiceConfigs = [];
  List<KeyValuePair> _textModels;
  final List<ServiceConfig> speechToTextServiceConfigs = [];
  List<KeyValuePair> _speechToTextModels;
  final List<ServiceConfig> textToSpeechServiceConfigs = [];
  List<KeyValuePair> _textToSpeechModels;
  List<KeyValuePair> _textToSpeechVoices;

  bool _initialized = false;
  String? _selectImageKey;
  ServiceConfig? _selectTextService;
  KeyValuePair? _selectTextModel;
  ServiceConfig? _selectSpeechToTextService;
  KeyValuePair? _selectSpeechToTextModel;
  ServiceConfig? _selectTextToSpeechService;
  KeyValuePair? _selectTextToSpeechModel;
  KeyValuePair? _selectTextToSpeechVoice;

  List<String> get imageKeys => _imageKeys;
  List<KeyValuePair> get textModels => _textModels;
  List<KeyValuePair> get speechToTextModels => _speechToTextModels;
  List<KeyValuePair> get textToSpeechModels => _textToSpeechModels;
  List<KeyValuePair> get textToSpeechVoices => _textToSpeechVoices;

  bool get initialized => _initialized;
  String? get selectImageKey => _selectImageKey;
  ServiceConfig? get selectTextService => _selectTextService;
  KeyValuePair? get selectTextModel => _selectTextModel;
  ServiceConfig? get selectSpeechToTextService => _selectSpeechToTextService;
  KeyValuePair? get selectSpeechToTextModel => _selectSpeechToTextModel;
  ServiceConfig? get selectTextToSpeechService => _selectTextToSpeechService;
  KeyValuePair? get selectTextToSpeechModel => _selectTextToSpeechModel;
  KeyValuePair? get selectTextToSpeechVoice => _selectTextToSpeechVoice;

  AgentConfigScreenViewModel(this._configStorage, {AgentConfig? agentConfig})
      : _id = agentConfig?.id,
        nameController = TextEditingController(text: agentConfig?.name ?? ''),
        _selectTextService = agentConfig?.textServiceConfig,
        _textModels = agentConfig?.textServiceConfig.textConfig?.models ?? [],
        _selectTextModel = agentConfig?.textModel,
        _selectSpeechToTextService = agentConfig?.speechToTextServiceConfig,
        _speechToTextModels =
            agentConfig?.speechToTextServiceConfig.speechToTextConfig?.models ??
                [],
        _selectSpeechToTextModel = agentConfig?.speechToTextModel,
        _selectTextToSpeechService = agentConfig?.textToSpeechServiceConfig,
        _textToSpeechModels =
            agentConfig?.textToSpeechServiceConfig.textToSpeechConfig?.models ??
                [],
        _selectTextToSpeechModel = agentConfig?.textToSpeechModel,
        _textToSpeechVoices =
            agentConfig?.textToSpeechServiceConfig.textToSpeechConfig?.voices ??
                [],
        _selectTextToSpeechVoice = agentConfig?.textToSpeechVoice;

  Future<void> initialize(ImageStorageRepository imageStorage) async {
    _imageKeys.addAll(await imageStorage.getImageNames());
    textServiceConfigs.addAll(await _configStorage.loadTextServiceConfigs());
    speechToTextServiceConfigs
        .addAll(await _configStorage.loadSpeechToTextServiceConfigs());
    textToSpeechServiceConfigs
        .addAll(await _configStorage.loadTextToSpeechServiceConfigs());
    _initialized = true;
    notifyListeners();
  }

  @override
  void dispose() {
    nameController.dispose();
    super.dispose();
  }

  void updateImageKey(String? imageKey) {
    _ensureInitialized();
    if (selectImageKey == imageKey) return;
    _selectImageKey = imageKey;
    notifyListeners();
  }

  void updateTextServiceConfig(ServiceConfig? config) {
    _ensureInitialized();
    if (selectTextService == config) return;
    _selectTextService = config;
    _textModels = config?.textConfig?.models ?? [];
    _selectTextModel = null;
    notifyListeners();
  }

  void updateSpeechToTextServiceConfig(ServiceConfig? config) {
    _ensureInitialized();
    if (selectSpeechToTextService == config) return;
    _selectSpeechToTextService = config;
    _speechToTextModels = config?.speechToTextConfig?.models ?? [];
    _selectSpeechToTextModel = null;
    notifyListeners();
  }

  void updateTextToSpeechServiceConfig(ServiceConfig? config) {
    _ensureInitialized();
    if (selectTextToSpeechService == config) return;
    _selectTextToSpeechService = config;
    _textToSpeechModels = config?.textToSpeechConfig?.models ?? [];
    _selectTextToSpeechModel = null;
    _textToSpeechVoices = config?.textToSpeechConfig?.voices ?? [];
    _selectTextToSpeechVoice = null;
    notifyListeners();
  }

  void updateTextModel(KeyValuePair? model) {
    _ensureInitialized();
    _selectTextModel = model;
    notifyListeners();
  }

  void updateSpeechToTextModel(KeyValuePair? model) {
    _ensureInitialized();
    _selectSpeechToTextModel = model;
    notifyListeners();
  }

  void updateTextToSpeechModel(KeyValuePair? model) {
    _ensureInitialized();
    _selectTextToSpeechModel = model;
    notifyListeners();
  }

  void updateTextToSpeechVoice(KeyValuePair? voice) {
    _ensureInitialized();
    _selectTextToSpeechVoice = voice;
    notifyListeners();
  }

  String? validationCheck() {
    _ensureInitialized();
    if (nameController.text.isEmpty) {
      return t.home.agent.error.nameIsRequired;
    }
    if (selectImageKey == null) {
      // TODO
      return t.home.agent.error.textServiceRequired;
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
    if (selectTextToSpeechModel == null) {
      return t.home.agent.error.textToSpeechModelRequired;
    }
    if (selectTextToSpeechVoice == null) {
      return t.home.agent.error.textToSpeechVoiceRequired;
    }
    return null;
  }

  AgentConfig createAgentConfig() {
    _ensureInitialized();
    return AgentConfig(
      id: _id,
      name: nameController.text,
      imagekey: selectImageKey!,
      textServiceConfig: selectTextService!,
      textModel: selectTextModel!,
      speechToTextServiceConfig: selectSpeechToTextService!,
      speechToTextModel: selectSpeechToTextModel!,
      textToSpeechServiceConfig: selectTextToSpeechService!,
      textToSpeechModel: selectTextToSpeechModel!,
      textToSpeechVoice: selectTextToSpeechVoice!,
    );
  }

  void _ensureInitialized() {
    if (!initialized) {
      throw UninitializedException(runtimeType.toString());
    }
  }
}
