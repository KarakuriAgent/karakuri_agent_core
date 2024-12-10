// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'dart:async';

import 'package:karakuri_agent/services/speech_to_text/speech_to_text_service.dart';
import 'package:speech_to_text/speech_recognition_result.dart';
import 'package:speech_to_text/speech_to_text.dart';

class SpeechToTextDeviceService extends SpeechToTextService {
  final SpeechToText _speech = SpeechToText();
  Completer<String>? _completer;
  bool _isListening = false;

  @override
  Future<void> init() async {
    await _speech.initialize(
      onStatus: (status) {
        if (status == 'notListening' && _isListening) {
          _startListening();
        }
      }
    );
  }

  @override
  Future<String> start() async {
    _completer = Completer<String>();
    _isListening = true;
    _startListening();
    return _completer!.future;
  }

  void _startListening() {
    _speech.listen(
        onResult: (SpeechRecognitionResult result) async {
          final recognizedWords = result.recognizedWords;
          if (recognizedWords.isNotEmpty &&
              _completer != null &&
              !_completer!.isCompleted) {
            _completer!.complete(recognizedWords);
            await stop();
          }
        },
        listenFor: const Duration(days: -1 >>> 1),
        listenOptions: SpeechListenOptions(
            cancelOnError: false,
            partialResults: false,
            onDevice: true,
            listenMode: ListenMode.dictation));
  }

  @override
  Future<void> stop() async {
    _isListening = false;
    if (_completer != null && !_completer!.isCompleted) {
      _completer!.complete("");
    }
    await _speech.stop();
  }

  @override
  Future<void> dispose() async {
    await stop();
  }
}
