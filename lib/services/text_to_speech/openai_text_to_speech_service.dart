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
  Completer<dynamic>? _cancelCompleter;

  OpenaiTextToSpeechService(this._agentConfig);

  @override
  void dispose() {
    _player.dispose();
    if (_cancelCompleter?.isCompleted == false) {
      _cancelCompleter?.complete(null);
    }
    _cancelCompleter = null;
  }

  @override
  Future<void> speech(String text) async {
    final completer = Completer();
    _cancelCompleter = Completer();
    final listen = _player.onPlayerComplete.listen((_) {
      completer.complete();
    });
    try {
      final bytes = await Future.any([
        _requestSpeech(text),
        _cancelCompleter?.future ?? Future<dynamic>.value(),
      ]);
      if (bytes == null) {
        throw CancellationException('OpenaiTextToSpeech');
      }
      await _player.play(BytesSource(bytes), mode: PlayerMode.mediaPlayer);
      await completer.future;
    } catch (e) {
      if (_cancelCompleter?.isCompleted ?? true) {
        rethrow;
      }
      throw ServiceException(runtimeType.toString(), 'speech');
    } finally {
      listen.cancel();
      _cancelCompleter = null;
    }
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

  @override
  void stop() {
    _player.stop();
    if (_cancelCompleter?.isCompleted == false) {
      _cancelCompleter?.complete(null);
    }
    _cancelCompleter = null;
  }
}
