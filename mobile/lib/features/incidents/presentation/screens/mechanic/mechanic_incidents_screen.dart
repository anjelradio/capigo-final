import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';

class MechanicIncidentsScreen extends StatelessWidget {
  const MechanicIncidentsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.appBgBase,
      appBar: AppBar(title: const Text('Historial mecanico')),
      body: const Center(
        child: Text(
          'Proximamente veras tus servicios completados y cancelados.',
          textAlign: TextAlign.center,
          style: TextStyle(color: AppColors.appTextOnDarkMuted),
        ),
      ),
    );
  }
}
