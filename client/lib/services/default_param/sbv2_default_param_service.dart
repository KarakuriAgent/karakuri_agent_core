import 'package:karakuri_agent/models/key_value_pair.dart';
import 'package:karakuri_agent/services/default_param/default_param_service.dart';

class Sbv2DefaultParamService extends DefaultParamService {
  @override
  List<KeyValuePair> get textModels => const [];

  @override
  List<KeyValuePair> get speechToTextModels => const [];

  @override
  List<KeyValuePair> get textToSpeechModels => const [
        KeyValuePair(key: '0', value: '0'),
      ];

  @override
  List<KeyValuePair> get textToSpeechVoices => const [
        KeyValuePair(key: '0', value: '0'),
      ];
}
