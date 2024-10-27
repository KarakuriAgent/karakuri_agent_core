import 'package:karakuri_agent/models/key_value_pair.dart';
import 'package:karakuri_agent/services/default_param/default_param_service.dart';

class VoicevoxNemoDefaultParamService extends DefaultParamService {
  @override
  List<KeyValuePair> get textModels => const [];

  @override
  List<KeyValuePair> get speechToTextModels => const [];

  @override
  List<KeyValuePair> get textToSpeechModels => const [
        KeyValuePair(key: 'default', value: 'default'),
      ];

  @override
  List<KeyValuePair> get textToSpeechVoices => const [
        KeyValuePair(key: '10005', value: '女声1:ノーマル'),
        KeyValuePair(key: '10007', value: '女声2:ノーマル'),
        KeyValuePair(key: '10004', value: '女声3:ノーマル'),
        KeyValuePair(key: '10003', value: '女声4:ノーマル'),
        KeyValuePair(key: '10008', value: '女声5:ノーマル'),
        KeyValuePair(key: '10006', value: '女声6:ノーマル'),
        KeyValuePair(key: '10001', value: '男声1:ノーマル'),
        KeyValuePair(key: '10000', value: '男声2:ノーマル'),
        KeyValuePair(key: '10002', value: '男声3:ノーマル'),
      ];
}
