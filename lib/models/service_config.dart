import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/models/speech_to_text_config.dart';
import 'package:karakuri_agent/models/text_config.dart';
import 'package:karakuri_agent/models/text_to_speech_config.dart';
import 'package:karakuri_agent/services/database/sqflite_helper.dart';

part 'service_config.freezed.dart';
part 'service_config.g.dart';

@freezed
class ServiceConfig with _$ServiceConfig {
  const ServiceConfig._();
  const factory ServiceConfig({
    @JsonKey(name: ColumnName.id) int? id,
    @JsonKey(name: ColumnName.name) required String name,
    @JsonKey(name: ColumnName.type) required ServiceType type,
    @JsonKey(name: ColumnName.baseUrl) required String baseUrl,
    @JsonKey(name: ColumnName.apiKey) required String apiKey,
    TextConfig? textConfig,
    TextToSpeechConfig? textToSpeechConfig,
    SpeechToTextConfig? speechToTextConfig,
  }) = _ServiceConfig;

  factory ServiceConfig.fromJson(Map<String, dynamic> json) =>
      _$ServiceConfigFromJson(json);

  Map<String, dynamic> toDatabaseMap() {
    return {
      ColumnName.id: id,
      ColumnName.name: name,
      ColumnName.type: type.name,
      ColumnName.baseUrl: baseUrl,
      ColumnName.apiKey: apiKey,
    };
  }
}
