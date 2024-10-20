import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:karakuri_agent/models/key_value_pair.dart';
import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/services/database/sqflite_helper.dart';

part 'agent_config.freezed.dart';
part 'agent_config.g.dart';

@freezed
class AgentConfig with _$AgentConfig {
  const AgentConfig._();
  const factory AgentConfig({
    @JsonKey(name: ColumnName.id) int? id,
    @JsonKey(name: ColumnName.name) required String name,
    required ServiceConfig textServiceConfig,
    required KeyValuePair textModel,
    required ServiceConfig speechToTextServiceConfig,
    required KeyValuePair speechToTextModel,
    required ServiceConfig textToSpeechServiceConfig,
    required KeyValuePair textToSpeechModel,
    required KeyValuePair textToSpeechVoice,
  }) = _AgentConfig;

  factory AgentConfig.fromJson(Map<String, dynamic> json) =>
      _$AgentConfigFromJson(json);

  Map<String, dynamic> toDatabaseMap() {
    final map = <String, dynamic>{
      ColumnName.name: name,
      ColumnName.textServiceId: textServiceConfig.id,
      ColumnName.textModelId: textModel.id,
      ColumnName.speechToTextServiceId: speechToTextServiceConfig.id,
      ColumnName.speechToTextModelId: speechToTextModel.id,
      ColumnName.textToSpeechServiceId: textToSpeechServiceConfig.id,
      ColumnName.textToSpeechModelId: textToSpeechModel.id,
      ColumnName.textToSpeechVoiceId: textToSpeechVoice.id,
    };
    if (id != null) {
      map[ColumnName.id] = id;
    }
    return map;
  }
}
