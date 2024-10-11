import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:karakuri_agent/models/key_value_pair.dart';
import 'package:karakuri_agent/services/database/sqflite_helper.dart';

part 'text_config.freezed.dart';
part 'text_config.g.dart';

@freezed
class TextConfig with _$TextConfig {
  const TextConfig._();
  const factory TextConfig({
    @JsonKey(name: ColumnName.id) int? id,
    @Default([]) List<KeyValuePair> models,
  }) = _TextConfig;

  factory TextConfig.fromJson(Map<String, dynamic> json) =>
      _$TextConfigFromJson(json);

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
