import 'dart:typed_data';

abstract class SpeechToTextService {
  Future<String> createTranscription(Uint8List audio);
}
