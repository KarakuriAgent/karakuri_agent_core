import 'dart:async';

import 'package:karakuri_agent/services/speech/speech_service.dart';

class SpeechRepository {
  final SpeechService _service;

  SpeechRepository(this._service);

  Future<bool> play(String url) async {
    return await _service.play(url);
  }

  Future<void> dispose() async {
    _service.dispose();
  }

  Future<void> stop() async {
    _service.stop();
  }
}
