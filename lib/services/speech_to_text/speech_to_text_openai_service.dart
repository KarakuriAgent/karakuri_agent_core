import 'dart:convert';
import 'dart:typed_data';

import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/services/speech_to_text/speech_to_text_service.dart';
import 'package:http/http.dart' as http;

class SpeechToTextOpenaiService extends SpeechToTextService {
  final AgentConfig _agentConfig;

  SpeechToTextOpenaiService(this._agentConfig);

  @override
  Future<String> createTranscription(Uint8List audio) async {
    final serviceConfig = _agentConfig.speechToTextServiceConfig;
    final url = Uri.parse('${serviceConfig.baseUrl}/audio/transcriptions');
    final request = http.MultipartRequest('POST', url);
    request.headers['Authorization'] = 'Bearer ${serviceConfig.apiKey}';
    request.headers['Content-Type'] = 'multipart/form-data';
    request.fields['model'] = _agentConfig.speechToTextModel.value;
    request.files.add(http.MultipartFile.fromBytes(
      'file',
      audio,
      filename: 'audio.wav',
    ));

    try {
      final response = await request.send();
      if (response.statusCode == 200) {
        final responseBody = await response.stream.bytesToString();
        final jsonResponse = json.decode(responseBody);
        return jsonResponse['text'];
      } else {
        return 'Error: ${response.statusCode}: ${response.toString()}';
      }
    } catch (e) {
      return 'Error: $e';
    }
  }
}
