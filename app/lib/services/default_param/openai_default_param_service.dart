import 'package:karakuri_agent/models/key_value_pair.dart';
import 'package:karakuri_agent/services/default_param/default_param_service.dart';

class OpenAIDefaultParamService extends DefaultParamService {
  @override
  List<KeyValuePair> get textModels => const [
        KeyValuePair(key: 'gpt-4o', value: 'gpt-4o'),
        KeyValuePair(key: 'gpt-4o-mini', value: 'gpt-4o-mini'),
      ];

  @override
  List<KeyValuePair> get speechToTextModels => const [
        KeyValuePair(key: 'whisper-1', value: 'whisper-1'),
      ];

  @override
  List<KeyValuePair> get textToSpeechModels => const [
        KeyValuePair(key: 'tts-1', value: 'tts-1'),
        KeyValuePair(key: 'tts-1-hd', value: 'tts-1-hd'),
      ];

  @override
  List<KeyValuePair> get textToSpeechVoices => const [
        KeyValuePair(key: 'alloy', value: 'Alloy'),
        KeyValuePair(key: 'echo', value: 'Echo'),
        KeyValuePair(key: 'fable', value: 'Fable'),
        KeyValuePair(key: 'nova', value: 'Nova'),
        KeyValuePair(key: 'onyx', value: 'Onyx'),
        KeyValuePair(key: 'shimmer', value: 'Shimmer'),
      ];
}
