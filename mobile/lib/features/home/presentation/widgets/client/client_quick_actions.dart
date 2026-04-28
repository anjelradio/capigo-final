import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile/features/home/presentation/widgets/shared/shared_widgets.dart';
import 'package:mobile/features/home/presentation/widgets/client/my_vehicles_sheet.dart';
import 'package:mobile/features/incidents/presentation/providers/providers.dart';
import 'package:mobile/features/incidents/presentation/widgets/widgets.dart';

class ClientQuickActions extends StatelessWidget {
  const ClientQuickActions({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: ActionBarButton(
                title: 'Mis vehiculos',
                imagePath: 'assets/images/buttons/client/my_vehicles.png',
                onTap: () => showMyVehiclesSheet(context),
              ),
            ),
            SizedBox(width: 12),
            Expanded(
              child: ActionBarButton(
                title: 'Servicios realizados',
                imagePath: 'assets/images/buttons/client/done.png',
                onTap: () => _openServicesSheet(
                  context,
                  mode: ClientServicesListMode.completed,
                ),
              ),
            ),
          ],
        ),
        SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: ActionBarButton(
                title: 'Servicios en curso',
                imagePath: 'assets/images/buttons/client/services.png',
                onTap: () => context.push('/incidents/active-service'),
              ),
            ),
            SizedBox(width: 12),
            Expanded(
              child: ActionBarButton(
                title: 'Historial de servicios',
                imagePath: 'assets/images/buttons/client/historial.png',
                onTap: () => _openServicesSheet(
                  context,
                  mode: ClientServicesListMode.history,
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
    required ClientServicesListMode mode,
  }) async {
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => ClientServicesSheet(mode: mode),
    );
  }
}
