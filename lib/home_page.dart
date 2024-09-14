import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/providers/shared_preferences.dart';

class MyHomePage extends HookConsumerWidget {
  const MyHomePage({super.key, required this.title});
  final String title;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sharedPref = ref.watch(sharedPreferencesProvider);

    final counterState = useState<int?>(null);

    useEffect(() {
      sharedPref.getInt('counter').then((value) {
        counterState.value = value ?? 0;
      });
      return null;
    }, []);

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text(
              'You have pushed the button this many times:',
            ),
            if (counterState.value == null)
              const CircularProgressIndicator()
            else
              Text(
                '${counterState.value}',
                style: Theme.of(context).textTheme.headlineMedium,
              ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          if (counterState.value != null) {
            counterState.value = counterState.value! + 1;
            await sharedPref.setInt('counter', counterState.value!);
          }
        },
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ),
    );
  }
}
