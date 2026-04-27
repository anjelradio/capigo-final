import 'package:flutter/material.dart';

class VehicleCreateScreen extends StatelessWidget {
  const VehicleCreateScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Crear vehiculo')),
      body: const Center(
        child: Text(
          'Aqui ira la pantalla para crear vehiculos.',
          style: TextStyle(
            color: Color(0xFF1E2C39),
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }
}
