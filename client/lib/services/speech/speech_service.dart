import 'dart:async';

abstract class SpeechService {
  Future<bool> play(String url);
  Future<void> stop();
  Future<void> dispose();
}
