import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/repositories/speech_to_text_repository.dart';

part 'speech_to_text_provider.freezed.dart';

@freezed
class SpeechToTextProviderParam with _$SpeechToTextProviderParam {
  const SpeechToTextProviderParam._();
  const factory SpeechToTextProviderParam({
    required AgentConfig agentConfig,
    required Function(String)? onResult,
  }) = _SpeechToTextProviderParam;
}

final speechToTextProvider = FutureProvider.autoDispose
    .family<SpeechToTextRepository, SpeechToTextProviderParam>((ref, param) async {
  final speechToTextRepository = SpeechToTextRepository(ref, param);
  await speechToTextRepository.init();
  ref.onDispose(() {
    speechToTextRepository.dispose();
  });
  return speechToTextRepository;
});
