import 'dart:typed_data';

abstract class SileroVadServiceInterface {
  Future<void> create(Function(Uint8List) onResult);
  bool isCreated();
  bool listening();
  Future<void> start();
  Future<void> pause();
  Future<void> destroy();
}
