import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:karakuri_agent/services/database/sqflite_helper.dart';

part 'key_value_pair.freezed.dart';
part 'key_value_pair.g.dart';

@freezed
class KeyValuePair with _$KeyValuePair {
  const KeyValuePair._();
  const factory KeyValuePair({
    @JsonKey(name: ColumnName.id) int? id,
    @JsonKey(name: ColumnName.key) required String key,
    @JsonKey(name: ColumnName.value) required String value,
  }) = _KeyValuePair;

  factory KeyValuePair.fromJson(Map<String, dynamic> json) =>
      _$KeyValuePairFromJson(json);

  Map<String, dynamic> toDatabaseMap(String parrentIdColumnName, int parentId) {
    final map = <String, dynamic>{
      parrentIdColumnName: parentId,
      ColumnName.key: key,
      ColumnName.value: value
    };
    if (id != null) {
      map[ColumnName.id] = id;
    }
    return map;
  }
}
