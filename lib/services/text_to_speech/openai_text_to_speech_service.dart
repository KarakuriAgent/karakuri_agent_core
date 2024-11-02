import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:audioplayers/audioplayers.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:http/http.dart' as http;
import 'package:karakuri_agent/services/text_to_speech/text_to_speech_service.dart';
import 'package:karakuri_agent/utils/exception.dart';

class OpenaiTextToSpeechService extends TextToSpeechService {
  final AgentConfig _agentConfig;
  final _player = AudioPlayer();
  Completer<Uint8List?>? _synthesizeCompleter;

  OpenaiTextToSpeechService(this._agentConfig);

  @override
  Future<Uint8List> synthesize(String text) async {
    _synthesizeCompleter = Completer();
    try {
      final bytes = await Future.any([
        _requestSpeech(text),
        _synthesizeCompleter?.future ?? Future<Uint8List?>.value(null),
      ]);
      if (bytes == null) {
        throw CancellationException('OpenaiTextToSpeech');
      }
      return bytes;
    } catch (e) {
      _synthesizeCompleter?.completeError(e);
      rethrow;
    } finally {
      _synthesizeCompleter = null;
    }
  }

  @override
  Future<void> play(Uint8List audioData) async {
    Completer<void>? playCompleter = Completer();
    final listen = _player.onPlayerComplete.listen((_) {
      playCompleter.complete();
    });

    try {
      await _player.play(BytesSource(audioData), mode: PlayerMode.mediaPlayer);
      await playCompleter.future;
    } catch (e) {
      playCompleter.completeError(e);
      rethrow;
    } finally {
      listen.cancel();
    }
  }

  @override
  void stop() {
    _player.stop();
    _cleanupCancelCompleter();
  }

  @override
  void dispose() {
    _player.stop();
    _player.dispose();
    _cleanupCancelCompleter();
  }

  Future<Uint8List> _requestSpeech(String text) async {
    final config = _agentConfig.textToSpeechServiceConfig;

    final headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ${config.apiKey}',
    };

    final data = {
      'model': _agentConfig.textToSpeechModel.key,
      'voice': _agentConfig.textToSpeechVoice.key,
      'input': text
    };

    try {
      final response = await http.post(
        Uri.parse('${config.baseUrl}/audio/speech'),
        headers: headers,
        body: jsonEncode(data),
      );

      if (response.statusCode == 200 && response.body.isNotEmpty) {
        return response.bodyBytes;
      } else {
        final errorResponse = response.body;
        final errorMessage = json.decode(errorResponse)['error']['message'];
        throw Exception('HTTP ${response.statusCode}: $errorMessage');
      }
    } catch (e) {
      throw Exception('An unexpected error occurred during text-to-speech.');
    }
  }

  void _cleanupCancelCompleter() {
    if (_synthesizeCompleter?.isCompleted == false) {
      _synthesizeCompleter?.complete(null);
    }
    _synthesizeCompleter = null;
  }
}
