// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'dart:async';

import 'package:audioplayers/audioplayers.dart';
import 'package:karakuri_agent/services/speech/speech_service.dart';

class SpeechAudioPlayerService extends SpeechService {
  final _player = AudioPlayer();

  @override
  Future<bool> play(String url) async {
    final completer = Completer<bool>();
    StreamSubscription? subscription;
    subscription = _player.onPlayerStateChanged.listen((event) {
      if (event == PlayerState.stopped || event == PlayerState.disposed) {
        completer.complete(false);
        subscription?.cancel();
      } else if (event == PlayerState.completed) {
        completer.complete(true);
        subscription?.cancel();
      }
    });
    await _player.play(UrlSource(url), mode: PlayerMode.mediaPlayer);
    return completer.future;
  }

  @override
  Future<void> stop() async {
    await _player.stop();
  }

  @override
  Future<void> dispose() async {
    await _player.dispose();
  }
}
