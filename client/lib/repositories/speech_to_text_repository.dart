// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'dart:async';

import 'package:karakuri_agent/services/speech_to_text/speech_to_text_service.dart';
import 'package:karakuri_agent/utils/exception.dart';

class SpeechToTextRepository {
  final SpeechToTextService _service;
  final _initializedCompleter = Completer<void>();

  SpeechToTextRepository(this._service);

  Future<void> init() async {
    await _service.init();
    _initializedCompleter.complete();
  }

  Future<String> start() async {
    await _ensureInitialized();
    return await _service.start();
  }

  Future<void> dispose() async {
    await _ensureInitialized();
    await _service.dispose();
  }

  Future<void> stop() async {
    await _ensureInitialized();
    await _service.stop();
  }

  Future<void> _ensureInitialized() async {
    try {
      await _initializedCompleter.future.timeout(Duration(seconds: 5));
    } on TimeoutException {
      throw UninitializedException(runtimeType.toString());
    }
  }
}
