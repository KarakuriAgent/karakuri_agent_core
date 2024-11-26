import 'package:karakuri_agent/models/key_value_pair.dart';
import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/services/default_param/default_param_service.dart';
import 'package:karakuri_agent/services/default_param/openai_default_param_service.dart';
import 'package:karakuri_agent/services/default_param/sbv2_default_param_service.dart';
import 'package:karakuri_agent/services/default_param/voicevox_default_param_service.dart';
import 'package:karakuri_agent/services/default_param/voicevox_nemo_default_param_service.dart';

class DefaultParamRepository {
  final DefaultParamService _defaultParamService;

  DefaultParamRepository(ServiceType serviceType)
      : _defaultParamService = switch (serviceType) {
          ServiceType.openAI => OpenAIDefaultParamService(),
          ServiceType.voicevox => VoicevoxDefaultParamService(),
          ServiceType.voicevoxNemo => VoicevoxNemoDefaultParamService(),
          ServiceType.styleBertVITS2 => Sbv2DefaultParamService(),
        };

  List<KeyValuePair> get textModels => _defaultParamService.textModels;

  List<KeyValuePair> get speechToTextModels =>
      _defaultParamService.speechToTextModels;

  List<KeyValuePair> get textToSpeechModels =>
      _defaultParamService.textToSpeechModels;

  List<KeyValuePair> get textToSpeechVoices =>
      _defaultParamService.textToSpeechVoices;
}
