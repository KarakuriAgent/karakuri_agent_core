// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'dart:async';

import 'package:karakuri_agent/services/speech/speech_service.dart';

class SpeechRepository {
  final SpeechService _service;

  SpeechRepository(this._service);

  Future<bool> play(String url) async {
    return await _service.play(url);
  }

  Future<void> dispose() async {
    await _service.dispose();
  }

  Future<void> stop() async {
    await _service.stop();
  }
}
