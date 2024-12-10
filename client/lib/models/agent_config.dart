// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:karakuri_agent/services/database/sqflite_helper.dart';

part 'agent_config.freezed.dart';
part 'agent_config.g.dart';

@freezed
class AgentConfig with _$AgentConfig {
  const AgentConfig._();
  const factory AgentConfig(
          {@JsonKey(name: ColumnName.id) int? id,
          @JsonKey(name: ColumnName.name) required String name,
          @JsonKey(name: ColumnName.baseUrl) required String baseUrl,
          @JsonKey(name: ColumnName.apiKey) required String apiKey,
          @JsonKey(name: ColumnName.imageKey) required String imageKey,
          @JsonKey(name: ColumnName.agentId) required String agentId}) =
      _AgentConfig;

  factory AgentConfig.fromJson(Map<String, dynamic> json) =>
      _$AgentConfigFromJson(json);

  Map<String, dynamic> toDatabaseMap() {
    final map = <String, dynamic>{
      ColumnName.name: name,
      ColumnName.imageKey: imageKey,
      ColumnName.baseUrl: baseUrl,
      ColumnName.apiKey: apiKey,
      ColumnName.agentId: agentId
    };
    if (id != null) {
      map[ColumnName.id] = id;
    }
    return map;
  }

  static AgentConfig fromDatabaseMap(Map<String, dynamic> map) {
    return AgentConfig(
      id: map[ColumnName.id] as int,
      name: map[ColumnName.name] as String,
      baseUrl: map[ColumnName.baseUrl] as String,
      apiKey: map[ColumnName.apiKey] as String,
      imageKey: map[ColumnName.imageKey] as String,
      agentId: map[ColumnName.agentId] as String,
    );
  }
}
