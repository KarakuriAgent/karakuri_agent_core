import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/providers/voice_activity_detection_provider.dart';
import 'package:karakuri_agent/views/custom_view/link_text.dart';
import 'package:karakuri_agent/i18n/strings.g.dart';
import 'package:karakuri_agent/views/service_settings_screen.dart';

class HomeScreen extends HookConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final audioCallback = useCallback((audio) {
      print(audio.toString());
    }, []);
    final voiceActivityDetection =
        ref.watch(voiceActivityDetectionProvider(audioCallback));
    return Scaffold(
      appBar: AppBar(
        title: Text(t.home.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            LinkText(
              text: t.settings.serviceSettings.title,
              onTap: () async {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const ServiceSettingsScreen(),
                  ),
                );
              },
            ),
            ElevatedButton(
                onPressed: !voiceActivityDetection.hasValue
                    ? null
                    : () {
                        if (voiceActivityDetection.value!.listening()) {
                          print('pause');
                          voiceActivityDetection.value!.pause();
                        } else {
                          print('start');
                          voiceActivityDetection.value!.start();
                        }
                      },
                child:
                    Text(!voiceActivityDetection.hasValue ? 'loading' : 'VoiceActivityDetection')),
          ],
        ),
      ),
    );
  }
}
