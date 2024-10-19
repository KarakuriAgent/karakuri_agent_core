import 'package:karakuri_agent/models/text_message.dart';

abstract class TextService {
  Future<TextMessage> completions(List<TextMessage> messages);
}
