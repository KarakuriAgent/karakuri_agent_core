import 'package:karakuri_agent/models/key_value_pair.dart';
import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/services/default_param/default_param_service.dart';
import 'package:karakuri_agent/services/default_param/openai_default_param_service.dart';
import 'package:karakuri_agent/services/default_param/voicevox_default_param_service.dart';
import 'package:karakuri_agent/services/default_param/voicevox_nemo_default_param_service.dart';

class DefaultParamRepository {
  late final DefaultParamService _defaultParamService;

  DefaultParamRepository(ServiceType serviceType) {
    switch (serviceType) {
      case ServiceType.openAI:
        _defaultParamService = OpenAIDefaultParamService();
        break;
      case ServiceType.voicevox:
        _defaultParamService = VoicevoxDefaultParamService();
        break;
      case ServiceType.voicevoxNemo:
        _defaultParamService = VoicevoxNemoDefaultParamService();
        break;
      default:
        throw Exception(
            'Unsupported Text-to-Speech service type: $serviceType');
    }
  }

  List<KeyValuePair> get textModels => _defaultParamService.textModels;

  List<KeyValuePair> get speechToTextModels =>
      _defaultParamService.speechToTextModels;

  List<KeyValuePair> get textToSpeechModels =>
      _defaultParamService.textToSpeechModels;

  List<KeyValuePair> get textToSpeechVoices =>
      _defaultParamService.textToSpeechVoices;
}
