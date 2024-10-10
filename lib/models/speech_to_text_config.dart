import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:karakuri_agent/models/key_value_pair.dart';
import 'package:karakuri_agent/services/database/sqflite_helper.dart';

part 'speech_to_text_config.freezed.dart';
part 'speech_to_text_config.g.dart';

@freezed
class SpeechToTextConfig with _$SpeechToTextConfig {
  const SpeechToTextConfig._();
  const factory SpeechToTextConfig({
    @JsonKey(name: ColumnName.id) int? id,
    @Default([]) List<KeyValuePair> models,
  }) = _SpeechToTextConfig;
  factory SpeechToTextConfig.fromJson(Map<String, dynamic> json) =>
      _$SpeechToTextConfigFromJson(json);

  Map<String, dynamic> toDatabaseMap(int serviceConfigId) {
    return {
      ColumnName.id: id,
      ColumnName.serviceConfigId: serviceConfigId,
    };
  }
}