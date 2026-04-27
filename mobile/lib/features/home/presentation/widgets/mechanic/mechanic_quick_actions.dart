import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile/features/home/presentation/widgets/shared/shared_widgets.dart';

class MechanicQuickActions extends StatelessWidget {
  const MechanicQuickActions({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: ActionBarButton(
                title: 'Historial de servicios',
                imagePath: 'assets/images/buttons/client/historial.png',
                onTap: () => context.push('/incidents/mechanic'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: ActionBarButton(
                title: 'Mi perfil',
                imagePath: 'assets/images/buttons/client/my_vehicles.png',
                onTap: () => context.push('/user'),
              ),
            ),
          ],
        ),
      ],
    );
  }
}
