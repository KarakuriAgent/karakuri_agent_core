import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:audioplayers/audioplayers.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/utils/exception.dart';
import 'package:http/http.dart' as http;

class KarakuriService {
  final AgentConfig _agentConfig;
  final _player = AudioPlayer();
  Completer<Uint8List?>? _cancelCompleter;

  KarakuriService(this._agentConfig);

  Future<void> chat(String text) async {
    final completer = Completer();
    _cancelCompleter = Completer();
    final listen = _player.onPlayerComplete.listen((_) {
      completer.complete();
    });
    try {
      final Uint8List? bytes = await Future.any([
        _chat(text),
        _cancelCompleter?.future ?? Future<Uint8List?>.value(null),
      ]);
      if (bytes == null) {
        throw CancellationException('Sbv2TextToSpeech');
      }
      await _player.play(BytesSource(bytes), mode: PlayerMode.mediaPlayer);
      await completer.future;
    } on CancellationException {
      rethrow;
    } finally {
      listen.cancel();
      _cancelCompleter = null;
    }
  }

  void stop() {
    _player.stop();
    _cleanupCancelCompleter();
  }

  void dispose() {
    _player.dispose();
    _cleanupCancelCompleter();
  }

  Future<Uint8List> _chat(String text) async {
    final serviceConfig = _agentConfig.textToSpeechServiceConfig;
    final headers = {
      'X-API-Key': serviceConfig.apiKey,
      'accept': 'application/json',
      'Content-Type': 'application/json'
    };
      final response = await http.post(
        Uri.parse(
            '${serviceConfig.baseUrl}/v1/chat'),
        headers: headers,
        body: jsonEncode({
          "agent_id" : _agentConfig.textToSpeechVoice.key,
          "message": text
        })
      );
      if (response.statusCode == 200 && response.bodyBytes.isNotEmpty) {
        return response.bodyBytes;
      } else {
        final errorResponse = response.body;
        final errorMessage = json.decode(errorResponse)['error']['message'];
        throw Exception('HTTP ${response.statusCode}: $errorMessage');
      }
  }

  void _cleanupCancelCompleter() {
    if (_cancelCompleter?.isCompleted == false) {
      _cancelCompleter?.complete(null);
    }
    _cancelCompleter = null;
  }
}
