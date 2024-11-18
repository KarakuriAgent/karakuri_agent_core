import 'dart:async';
import 'dart:io';
import 'dart:typed_data';

import 'package:audio_streamer/audio_streamer.dart';
import 'package:flutter/services.dart';
import 'package:flutter_silero_vad/flutter_silero_vad.dart';
import 'package:karakuri_agent/services/silero_vad/silero_vad_service_interface.dart';
import 'package:karakuri_agent/utils/audio_util.dart';
import 'package:karakuri_agent/utils/exception.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';

// TODO パーミッションチェック
class SileroVadService extends SileroVadServiceInterface {
  static const int _sampleRate = 16000;
  static const int _frameSize = 40;
  static const int _bufferTimeInMilliseconds = 700;
  static const int _minAudioDurationMs = 100;

  final AudioStreamer _recorder = AudioStreamer.instance;
  final FlutterSileroVad _vad = FlutterSileroVad();
  final List<int> _lastAudioData = <int>[];
  final List<int> _audioDataBuffer = <int>[];
  final List<int> _frameBuffer = <int>[];

  DateTime? _lastActiveTime;
  StreamSubscription<List<int>>? _recordingDataSubscription;
  Function(Uint8List)? _onResult;
  bool _created = false;
  bool _isListening = false;

  Future<String> get _modelPath async =>
      '${(await getApplicationSupportDirectory()).path}/silero_vad.v5.onnx';

  @override
  Future<void> create(Function(Uint8List) onResult) async {
    _onResult = onResult;
    try {
      await _copyOnnxModelToLocal();
    } catch (e) {
      throw ServiceException(runtimeType.toString(), 'create',
          message: 'Failed to copy VAD model: $e');
    }
    await _vad.initialize(
      modelPath: await _modelPath,
      sampleRate: _sampleRate,
      frameSize: _frameSize,
      threshold: 0.7,
      minSilenceDurationMs: 100,
      speechPadMs: 0,
    );
    _created = true;
  }

  @override
  bool isCreated() => _created;

  @override
  Future<bool> start() async {
    return await _requestPermission();
  }

  Future<bool> _requestPermission() async {
    var status = await Permission.microphone.status;
    if (status.isGranted) {
      _startRecording();
    } else {
      Map<Permission, PermissionStatus> statuses = await [
        Permission.microphone,
      ].request();
      if (statuses[Permission.microphone] == PermissionStatus.granted) {
        _startRecording();
      } else if (await Permission.speech.isPermanentlyDenied) {
        openAppSettings();
        return false;
      } else {
        return await _requestPermission();
      }
    }
    return true;
  }

  Future<void> _startRecording() async {
    if (_isListening || !_created) return;

    _isListening = true;
    await _recorder.startRecording();

    _recordingDataSubscription = _recorder.audioStream.listen((buffer) async {
      final data = _transformBuffer(buffer);
      if (data.isEmpty) return;

      _frameBuffer.addAll(buffer);

      while (_frameBuffer.length >= _frameByteSize) {
        final frame = _frameBuffer.sublist(0, _frameByteSize);
        _frameBuffer.removeRange(0, _frameByteSize);
        await _processAudioFrame(frame);
      }
    });
  }

  @override
  bool listening() => _isListening;

  @override
  Future<void> pause() async {
    if (!_isListening) return;
    _audioDataBuffer.clear();
    await _recorder.stopRecording();
    await _recordingDataSubscription?.cancel();
    _isListening = false;
  }

  @override
  Future<void> destroy() async {
    await _recorder.stopRecording();
    await _recordingDataSubscription?.cancel();
    _recordingDataSubscription = null;
    _onResult = null;
    _isListening = false;
  }

  int get _frameByteSize => _frameSize * 2 * _sampleRate ~/ 1000;

  Future<void> _copyOnnxModelToLocal() async {
    final data =
        await rootBundle.load('assets/silero_models/silero_vad.v5.onnx');
    final bytes =
        data.buffer.asUint8List(data.offsetInBytes, data.lengthInBytes);
    final modelFile = File(await _modelPath);
    await modelFile.writeAsBytes(bytes);
  }

  Int16List _transformBuffer(List<int> buffer) {
    return Int16List.view(Uint8List.fromList(buffer).buffer);
  }

  Future<void> _processAudioFrame(List<int> buffer) async {
    final pcmData = _transformBuffer(buffer);
    final audioFloat32 = pcmData.map((e) => e / 32768.0).toList();

    final isSpeech = await _vad.predict(Float32List.fromList(audioFloat32));

    if (isSpeech ?? false) {
      _handleSpeechDetected(buffer);
    } else {
      _handleSilenceDetected(buffer);
    }
  }

  void _handleSpeechDetected(List<int> buffer) {
    _lastActiveTime = DateTime.now();
    _audioDataBuffer
      ..addAll(_lastAudioData)
      ..addAll(buffer);
    _lastAudioData.clear();
  }

  void _handleSilenceDetected(List<int> buffer) {
    if (_lastActiveTime != null) {
      _audioDataBuffer.addAll(buffer);
      if (DateTime.now().difference(_lastActiveTime!) >
          Duration(milliseconds: _bufferTimeInMilliseconds)) {
        if (_audioDataBuffer.length >=
            (_sampleRate * _minAudioDurationMs ~/ 1000)) {
          final wavData = _createWaveData(_audioDataBuffer);
          _onResult?.call(wavData);
          _stopRecording();
        }
        _audioDataBuffer.clear();
        _lastActiveTime = null;
      }
    } else {
      _lastAudioData.addAll(buffer);
      _trimLastAudioData();
    }
  }

  void _trimLastAudioData() {
    final maxLength = _sampleRate * 500 ~/ 1000;
    if (_lastAudioData.length > maxLength) {
      _lastAudioData.removeRange(0, _lastAudioData.length - maxLength);
    }
  }

  Future<void> _stopRecording() async {
    await _recordingDataSubscription?.cancel();
    await _recorder.stopRecording();
  }

  Uint8List _createWaveData(List<int> buffer) {
    final float32Data = _pcmBufferToFloat32List(buffer);
    return AudioUtil.float32ListToWav(float32Data, sampleRate: _sampleRate);
  }

  Float32List _pcmBufferToFloat32List(List<int> buffer) {
    final int16Data = Int16List.view(Uint8List.fromList(buffer).buffer);
    final float32Data = Float32List(int16Data.length);
    for (int i = 0; i < int16Data.length; i++) {
      float32Data[i] = int16Data[i] / 32768.0;
    }
    return float32Data;
  }
}
