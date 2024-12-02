import 'dart:typed_data';

class AudioUtil {
  static Uint8List float32ListToWav(Float32List float32List,
      {int sampleRate = 16000}) {
    final int byteRate = sampleRate * 2;
    final int totalDataLen = float32List.length * 2 + 36;

    final ByteData buffer = ByteData(44 + float32List.length * 2);

    _writeString(buffer, 0, 'RIFF');
    buffer.setUint32(4, totalDataLen, Endian.little);
    _writeString(buffer, 8, 'WAVE');
    _writeString(buffer, 12, 'fmt ');
    buffer.setUint32(16, 16, Endian.little);
    buffer.setUint16(20, 1, Endian.little);
    buffer.setUint16(22, 1, Endian.little);
    buffer.setUint32(24, sampleRate, Endian.little);
    buffer.setUint32(28, byteRate, Endian.little);
    buffer.setUint16(32, 2, Endian.little);
    buffer.setUint16(34, 16, Endian.little);
    _writeString(buffer, 36, 'data');
    buffer.setUint32(40, float32List.length * 2, Endian.little);

    _float32ToInt16(buffer, 44, float32List);

    return buffer.buffer.asUint8List();
  }

  static void _writeString(ByteData view, int offset, String string) {
    for (int i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.codeUnitAt(i));
    }
  }

  static void _float32ToInt16(ByteData output, int offset, Float32List input) {
    for (int i = 0; i < input.length; i++, offset += 2) {
      final double s = input[i];
      final int value =
          (s < 0 ? s * 32768 : s * 32767).toInt().clamp(-32768, 32767);
      output.setInt16(offset, value, Endian.little);
    }
  }
}
