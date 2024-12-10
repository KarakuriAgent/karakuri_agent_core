// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'package:freezed_annotation/freezed_annotation.dart';

part 'agent_response.freezed.dart';
part 'agent_response.g.dart';

@freezed
class AgentResponse with _$AgentResponse {
  const AgentResponse._();
  const factory AgentResponse({
    @JsonKey(name: "audio_url") required String audioUrl,
    @JsonKey(name: "dulation") required int duration,
    @JsonKey(name: "user_message") required String userMessage,
    @JsonKey(name: "agent_message") required String agentMessage,
    @JsonKey(name: "emotion") required Emotion emotion,
  }) = _AgentResponse;
  factory AgentResponse.fromJson(Map<String, dynamic> json) =>
      _$AgentResponseFromJson(json);
}

enum Emotion {
  noticed,
  progress,
  // Basic emotions
  happy,
  sad,
  angry,
  scared,
  surprised,
  disgusted,

  // Positive emotions
  excited,
  joyful,
  peaceful,
  grateful,
  proud,
  confident,
  amused,
  loving,

  // Negative emotions
  anxious,
  frustrated,
  disappointed,
  embarrassed,
  guilty,
  jealous,
  lonely,

  // Other emotional states
  neutral,
  confused,
  curious,
  determined,
  tired,
  energetic,
  hopeful,
  nostalgic,
  satisfied,
  bored,
  thoughtful,
  enthusiastic,
  relaxed,
  impressed,
  skeptical;

  String get key => toString().split('.').last;

  static Emotion fromString(String value) {
    return Emotion.values.firstWhere(
      (e) => e.key == value,
      orElse: () => Emotion.neutral,
    );
  }

  static List<String> toRequestValues() {
    return Emotion.values
        .where((e) => e != Emotion.noticed && e != Emotion.progress)
        .map((e) => e.key)
        .toList();
  }
}
