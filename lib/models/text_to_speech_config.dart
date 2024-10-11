import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:karakuri_agent/models/key_value_pair.dart';
import 'package:karakuri_agent/services/database/sqflite_helper.dart';

part 'text_to_speech_config.freezed.dart';
part 'text_to_speech_config.g.dart';

@freezed
class TextToSpeechConfig with _$TextToSpeechConfig {
  const TextToSpeechConfig._();
  const factory TextToSpeechConfig({
    @JsonKey(name: ColumnName.id) int? id,
    @Default([]) List<KeyValuePair> voices,
  }) = _TextToSpeechConfig;
  factory TextToSpeechConfig.fromJson(Map<String, dynamic> json) =>
      _$TextToSpeechConfigFromJson(json);

  Map<String, dynamic> toDatabaseMap(int serviceConfigId) {
    final map = <String, dynamic>{
      ColumnName.serviceConfigId: serviceConfigId,
    };
    if (id != null) {
      map[ColumnName.id] = id;
    }
    return map;
  }
}
