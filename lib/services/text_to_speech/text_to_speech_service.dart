import 'dart:typed_data';

abstract class TextToSpeechService {
   Future<Uint8List> synthesize(String text);
  Future<void> play(Uint8List audioData);
  void stop();
  void dispose();
}
