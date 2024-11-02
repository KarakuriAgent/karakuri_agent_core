import 'package:freezed_annotation/freezed_annotation.dart';

part 'text_result.freezed.dart';
part 'text_result.g.dart';

@freezed
class TextResult with _$TextResult {
  const TextResult._();
  const factory TextResult({
    required Emotion emotion,
    required String message,
  }) = _TextResult;
  factory TextResult.fromJson(Map<String, dynamic> json) =>
      _$TextResultFromJson(json);
}

enum Emotion {
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
      (e) => e.key.toLowerCase() == value.toLowerCase(),
      orElse: () => Emotion.neutral,
    );
  }
}
