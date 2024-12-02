import 'dart:typed_data';

import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:karakuri_agent/models/text_message.dart';

part 'karakuri_image.freezed.dart';

@freezed
class KarakuriImage with _$KarakuriImage {
  const KarakuriImage._();
  const factory KarakuriImage(
      {required Emotion emotion, required String extension, required Uint8List image}) = _KarakuriImage;
}
