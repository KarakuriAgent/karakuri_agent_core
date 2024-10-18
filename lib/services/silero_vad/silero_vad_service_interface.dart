import 'dart:typed_data';

abstract class SileroVadServiceInterface {
  Future<void> create(Function(Uint8List) end);
  bool isCreated();
  bool listening();
  void start();
  void pause();
  void destroy();
}
