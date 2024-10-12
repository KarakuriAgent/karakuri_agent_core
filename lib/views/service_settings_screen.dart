import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/providers/service_settings_screen_viewmodel_provider.dart';
import 'package:karakuri_agent/viewmodels/service_settings_screen_viewmodel.dart';
import 'package:karakuri_agent/views/service_config_screen.dart';
import 'package:karakuri_agent/i18n/strings.g.dart';

class ServiceSettingsScreen extends HookConsumerWidget {
  const ServiceSettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final viewModel = ref.watch(serviceSettingsScreenViewmodelProvider);
    final serviceConfigs = ref.watch(viewModel.serviceConfigsProvider);
    if (serviceConfigs == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    } else {
      return _ServiceSettingsContent(
        viewModel: viewModel,
        configs: serviceConfigs,
      );
    }
  }
}

class _ServiceSettingsContent extends HookConsumerWidget {
  final ServiceSettingsScreenViewmodel viewModel;
  final List<ServiceConfig> configs;

  const _ServiceSettingsContent(
      {required this.viewModel, required this.configs});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: Text(t.settings.serviceSettings.title),
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: configs.length,
              itemBuilder: (context, index) {
                final config = configs[index];
                return ServiceCard(
                  config: config,
                );
              },
            ),
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: OutlinedButton(
                child: Text(t.settings.serviceSettings.addService),
                onPressed: () async {
                  final serviceConfig = await Navigator.push(
                    context,
                    CupertinoPageRoute(
                      builder: (context) => const ServiceConfigScreen(),
                    ),
                  ) as ServiceConfig?;
                  if (serviceConfig != null) {
                    viewModel.addServiceConfig(serviceConfig);
                  }
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class ServiceCard extends HookConsumerWidget {
  final ServiceConfig config;

  const ServiceCard({super.key, required this.config});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final viewModel = ref.read(serviceSettingsScreenViewmodelProvider);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              t.settings.serviceSettings.name(name: config.name),
            ),
            Text(
              t.settings.serviceSettings
                  .serviceType(serviceType: config.type.displayName),
            ),
            Wrap(
              spacing: 8.0,
              children: viewModel
                  .getConfigTypes(config)
                  .map((cap) => Chip(label: Text(cap)))
                  .toList(),
            ),
            Row(
              children: [
                TextButton(
                  child: Text(t.settings.serviceSettings.editService),
                  onPressed: () async {
                    final serviceConfig = await Navigator.push(
                      context,
                      CupertinoPageRoute(builder: (context) {
                        return ServiceConfigScreen(initialConfig: config);
                      }),
                    ) as ServiceConfig?;
                    if (serviceConfig != null) {
                      viewModel.updateServiceConfig(serviceConfig);
                    }
                  },
                ),
                TextButton(
                  child: Text(t.settings.serviceSettings.deleteService),
                  onPressed: () async {
                    if (config.id != null) {
                      viewModel.deleteServiceConfig(config.id!);
                    }
                  },
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
