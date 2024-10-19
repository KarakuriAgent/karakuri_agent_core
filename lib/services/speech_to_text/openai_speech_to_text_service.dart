import 'dart:convert';
import 'dart:typed_data';

import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/services/speech_to_text/speech_to_text_service.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart'; 

class OpenaiSpeechToTextService extends SpeechToTextService {
  final AgentConfig _agentConfig;

  OpenaiSpeechToTextService(this._agentConfig);

  @override
  Future<String> createTranscription(Uint8List audio) async {
    final serviceConfig = _agentConfig.speechToTextServiceConfig;
    final url = Uri.parse('${serviceConfig.baseUrl}/audio/transcriptions');
    final request = http.MultipartRequest('POST', url);
    request.headers['Authorization'] = 'Bearer ${serviceConfig.apiKey}';
    request.fields['model'] = _agentConfig.speechToTextModel.key;
    request.files.add(http.MultipartFile.fromBytes(
      'file',
      audio,
      filename: 'audio.wav',
      contentType: MediaType('audio', 'wav'),
    ));

    try {
      final response = await request.send().timeout(const Duration(seconds: 10));
      if (response.statusCode == 200) {
        final responseBody = await response.stream.bytesToString();
        final jsonResponse = json.decode(responseBody);
        return jsonResponse['text'];
      } else {
        final errorResponse = await response.stream.bytesToString();
        final errorMessage = json.decode(errorResponse)['error']['message'];
        throw Exception('HTTP ${response.statusCode}: $errorMessage');
      }
    } catch (e) {
      throw Exception('An unexpected error occurred during transcription.');
    }
  }
}
