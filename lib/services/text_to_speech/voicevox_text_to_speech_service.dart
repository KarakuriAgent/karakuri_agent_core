import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:audioplayers/audioplayers.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/services/text_to_speech/text_to_speech_service.dart';
import 'package:http/http.dart' as http;
import 'package:karakuri_agent/utils/exception.dart';

class VoicevoxTextToSpeechService extends TextToSpeechService {
  final AgentConfig _agentConfig;
  final _player = AudioPlayer();
  Completer<Uint8List?>? _synthesizeCompleter;

  VoicevoxTextToSpeechService(this._agentConfig);

  @override
  Future<Uint8List> synthesize(String text) async {
    _synthesizeCompleter = Completer();
    try {
      final Uint8List? bytes;
      if (_agentConfig.textToSpeechServiceConfig.baseUrl ==
          'https://deprecatedapis.tts.quest/v2') {
        bytes = await Future.any([
          _voicevoxWebApi(text),
          _synthesizeCompleter?.future ?? Future<Uint8List?>.value(null),
        ]);
      } else {
        bytes = await Future.any([
          _voicevoxEngine(text),
          _synthesizeCompleter?.future ?? Future<Uint8List?>.value(null),
        ]);
      }
      if (bytes == null) {
        throw CancellationException('VoicevoxTextToSpeech');
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

  Future<Uint8List> _voicevoxWebApi(String text) async {
    final serviceConfig = _agentConfig.textToSpeechServiceConfig;

    try {
      final response = await http.get(
        Uri.parse(
            '${serviceConfig.baseUrl}/voicevox/audio/?key=${serviceConfig.apiKey}&speaker=${_agentConfig.textToSpeechVoice.key}&text=${Uri.encodeComponent(text)}'),
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

  Future<Uint8List> _voicevoxEngine(String text) async {
    final audioQuery = await _audioQuery(text);
    return await _synthesis(audioQuery);
  }

  Future<String> _audioQuery(String text) async {
    final serviceConfig = _agentConfig.textToSpeechServiceConfig;
    final headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ${serviceConfig.apiKey}',
    };

    try {
      var response = await http.post(
        Uri.parse(
            '${serviceConfig.baseUrl}/audio_query?text=${Uri.encodeComponent(text)}&speaker=${_agentConfig.textToSpeechVoice.key}'),
        headers: headers,
      );
      if (response.statusCode == 200 && response.body.isNotEmpty) {
        return response.body;
      } else {
        final errorResponse = response.body;
        final errorMessage = json.decode(errorResponse)['error']['message'];
        throw Exception('HTTP ${response.statusCode}: $errorMessage');
      }
    } catch (e) {
      throw Exception('An unexpected error occurred during text-to-speech.');
    }
  }

  Future<Uint8List> _synthesis(String accentPhrases) async {
    final serviceConfig = _agentConfig.textToSpeechServiceConfig;
    final headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ${serviceConfig.apiKey}',
    };

    try {
      final response = await http.post(
        Uri.parse(
            '${serviceConfig.baseUrl}/cancellable_synthesis?speaker=${_agentConfig.textToSpeechVoice.key}'),
        headers: headers,
        body: accentPhrases,
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
    if (_synthesizeCompleter?.isCompleted == false) {
      _synthesizeCompleter?.complete(null);
    }
    _synthesizeCompleter = null;
  }
}
