import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:audioplayers/audioplayers.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/services/text_to_speech/text_to_speech_service.dart';
import 'package:http/http.dart' as http;
import 'package:karakuri_agent/utils/exception.dart';

class Sbv2TextToSpeechService extends TextToSpeechService {
  final AgentConfig _agentConfig;
  final _player = AudioPlayer();
  Completer<Uint8List?>? _cancelCompleter;

  Sbv2TextToSpeechService(this._agentConfig);

  @override
  Future<void> speech(String text) async {
    final completer = Completer();
    _cancelCompleter = Completer();
    final listen = _player.onPlayerComplete.listen((_) {
      completer.complete();
    });
    try {
      final Uint8List? bytes = await Future.any([
        _voice(text),
        _cancelCompleter?.future ?? Future<Uint8List?>.value(null),
      ]);
      if (bytes == null) {
        throw CancellationException('Sbv2TextToSpeech');
      }
      await _player.play(BytesSource(bytes), mode: PlayerMode.mediaPlayer);
      await completer.future;
    } on CancellationException {
      rethrow;
    } catch (e) {
      throw ServiceException(runtimeType.toString(), 'speech');
    } finally {
      listen.cancel();
      _cancelCompleter = null;
    }
  }

  @override
  void stop() {
    _player.stop();
    _cleanupCancelCompleter();
  }

  @override
  void dispose() {
    _player.dispose();
    _cleanupCancelCompleter();
  }

  Future<Uint8List> _voice(String text) async {
    final serviceConfig = _agentConfig.textToSpeechServiceConfig;
    final headers = {
      'Authorization': 'Bearer ${serviceConfig.apiKey}',
    };

    try {
      final response = await http.post(
        Uri.parse(
            '${serviceConfig.baseUrl}/voice?text=$text&model_id=${_agentConfig.textToSpeechModel.key}&speaker_id=${_agentConfig.textToSpeechVoice.key}'),
        headers: headers,
      );
      if (response.statusCode == 200 && response.bodyBytes.isNotEmpty) {
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
    if (_cancelCompleter?.isCompleted == false) {
      _cancelCompleter?.complete(null);
    }
    _cancelCompleter = null;
  }
}
