import 'dart:async';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/services.dart';
import 'package:karakuri_agent/services/silero_vad/silero_vad_service_interface.dart';
import 'package:karakuri_agent/utils/audio_util.dart';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import 'package:sherpa_onnx/sherpa_onnx.dart' as sherpa_onnx;

class SileroVadService extends SileroVadServiceInterface {
  late sherpa_onnx.VoiceActivityDetector _vad;
  StreamSubscription<Uint8List>? _audioSubscription;
  bool _isCreated = false;
  bool _isListening = false;
  late Function(Uint8List) _onSpeechDetected;
  final _record = AudioRecorder();
  final List<double> _detectedSpeech = [];

  Future<String> _getModelPath() async {
    final appDir = await getApplicationDocumentsDirectory();
    final filePath = '${appDir.path}/silero_vad.onnx';
    final file = File(filePath);

    if (!await file.exists()) {
      final byteData =
          await rootBundle.load('assets/silero_models/silero_vad.v5.onnx');
      await file.writeAsBytes(byteData.buffer.asUint8List());
    }

    return filePath;
  }

  @override
  Future<void> create(Function(Uint8List) end) async {
    if (_isCreated) return;

    sherpa_onnx.initBindings();

    final sileroVadConfig =
        sherpa_onnx.SileroVadModelConfig(model: await _getModelPath());

    final config = sherpa_onnx.VadModelConfig(
      sileroVad: sileroVadConfig,
      numThreads: 1,
      debug: true,
    );

    _vad = sherpa_onnx.VoiceActivityDetector(
      config: config,
      bufferSizeInSeconds: 10,
    );

    _onSpeechDetected = end;
    _isCreated = true;
  }

  @override
  bool isCreated() => _isCreated;

  @override
  bool listening() => _isListening;

  @override
  void start() async {
    if (!_isCreated || _isListening) return;

    _isListening = true;

    // TODO audio permission request
    final stream = await _record.startStream(const RecordConfig());
    _audioSubscription = stream.listen((data) {
      _processAudio(data.buffer.asFloat32List());
    });
  }

  void _processAudio(Float32List samples) {
    _vad.acceptWaveform(samples);

    if (_vad.isDetected()) {
      while (!_vad.isEmpty()) {
        _detectedSpeech.addAll(samples);
        _vad.pop();
      }
      return;
    }
    if (_detectedSpeech.isNotEmpty) {
      final speechData = Float32List.fromList(_detectedSpeech);
      _detectedSpeech.clear();
      _onSpeechDetected(AudioUtil.float32ListToWav(speechData));
    }
  }

  @override
  void pause() async {
    if (!_isListening) return;
    _detectedSpeech.clear();
    _record.stop();
    _audioSubscription?.cancel();
    _isListening = false;
  }

  @override
  Future<void> destroy() async {
    if (!_isCreated) return;

    _isListening = false;
    _detectedSpeech.clear();
    await _record.stop();
    await _audioSubscription?.cancel();

    try {
      _vad.flush();
      while (!_vad.isEmpty()) {
        _vad.pop();
      }
    } finally {
      _vad.free();
      await _record.dispose();
      _isCreated = false;
    }
  }
}
