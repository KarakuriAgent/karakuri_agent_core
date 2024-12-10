import 'dart:typed_data';

import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:karakuri_agent/models/agent_response.dart';

part 'agent_image.freezed.dart';

@freezed
class AgentImage with _$AgentImage {
  const AgentImage._();
  const factory AgentImage(
      {required Emotion emotion, required String extension, required Uint8List image}) = _AgentImage;
}
