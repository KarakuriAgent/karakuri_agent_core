import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:audioplayers/audioplayers.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:http/http.dart' as http;
import 'package:karakuri_agent/services/text_to_speech/text_to_speech_service.dart';

class OpenaiTextToSpeechService extends TextToSpeechService {
  final AgentConfig _agentConfig;
  final _player = AudioPlayer();

  OpenaiTextToSpeechService(this._agentConfig);

  @override
  Future<void> speech(String text) async {
    final completer = Completer();
    final listen = _player.onPlayerComplete.listen((_) {
      completer.complete();
    });
    final bytes = await _requestSpeech(text);
    await _player.play(BytesSource(bytes), mode: PlayerMode.mediaPlayer);
    await completer.future;
    listen.cancel();
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

    final response = await http.post(
      Uri.parse('${config.baseUrl}/audio/speech'),
      headers: headers,
      body: jsonEncode(data),
    );

    if (response.statusCode == 200 && response.body.isNotEmpty) {
      return response.bodyBytes;
    } else {
      throw Exception('An unexpected error occurred during transcription.');
    }
  }
}
