import 'dart:io';
class LanguageUtil {
    static String get isoLanguageCode {
    String locale = Platform.localeName;
    List<String> parts = locale.split('_');
    return parts[0].split('.')[0];
  }
}
