import 'dart:async';

abstract class SpeechToTextService {
  Future<void> init();
  Future<String> start();
  Future<void> stop();
  Future<void> dispose();
}
