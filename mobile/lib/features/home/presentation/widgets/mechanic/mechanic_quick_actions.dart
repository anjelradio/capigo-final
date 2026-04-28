import 'package:flutter/material.dart';
import 'package:mobile/features/assignments/assignments.dart';
import 'package:mobile/features/home/presentation/widgets/shared/shared_widgets.dart';
import 'package:mobile/features/incidents/presentation/widgets/widgets.dart';

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
                title: 'Servicios completados',
                imagePath: 'assets/images/buttons/client/done.png',
                onTap: () => _openServicesSheet(
                  context,
                  mode: MechanicServicesMode.completed,
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: ActionBarButton(
                title: 'Historial de servicios',
                imagePath: 'assets/images/buttons/client/historial.png',
                onTap: () => _openServicesSheet(
                  context,
                  mode: MechanicServicesMode.history,
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Future<void> _openServicesSheet(
    BuildContext context, {
    required MechanicServicesMode mode,
  }) async {
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => MechanicServicesSheet(mode: mode),
    );
  }
}
