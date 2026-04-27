import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/assignments/domain/domain.dart';
import 'package:mobile/features/realtime/domain/domain.dart';

class MechanicActiveServiceInfoCard extends StatelessWidget {
  const MechanicActiveServiceInfoCard({
    super.key,
    required this.assignment,
    required this.realtimeSnapshot,
    required this.isUpdatingStatus,
    required this.onMarkOnTheWay,
    required this.onMarkArrived,
    required this.onMarkCompleted,
    required this.onCancel,
    required this.onOpenGoogleMaps,
  });

  final MechanicAssignment assignment;
  final IncidentRealtimeSnapshot? realtimeSnapshot;
  final bool isUpdatingStatus;
  final Future<void> Function() onMarkOnTheWay;
  final Future<void> Function() onMarkArrived;
  final Future<void> Function() onMarkCompleted;
  final Future<void> Function() onCancel;
  final Future<void> Function() onOpenGoogleMaps;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final currentStatus = _currentStatus();

    return Container(
      decoration: BoxDecoration(
        color: AppColors.appBgMid,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            assignment.incident.problemName ?? 'Servicio en curso',
            style: textTheme.bodyMedium?.copyWith(
              color: AppColors.appTextOnDark,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Estado: ${_statusLabel(currentStatus)}',
            style: textTheme.bodySmall?.copyWith(
              color: AppColors.appTextOnDarkMuted,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            assignment.incident.description?.trim().isNotEmpty == true
                ? assignment.incident.description!
                : 'Sin descripcion adicional del incidente.',
            style: textTheme.bodySmall?.copyWith(
              color: AppColors.appTextOnDarkMuted,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            assignment.incident.address?.trim().isNotEmpty == true
                ? assignment.incident.address!
                : 'Ubicacion sin direccion textual.',
            style: textTheme.bodySmall?.copyWith(
              color: AppColors.appTextOnDark,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            _vehicleText(),
            style: textTheme.bodySmall?.copyWith(
              color: AppColors.appTextOnDarkMuted,
              fontWeight: FontWeight.w600,
            ),
          ),
          if (assignment.incident.evidenceUrls.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(
              'Evidencias: ${assignment.incident.evidenceUrls.length} foto(s)',
              style: textTheme.bodySmall?.copyWith(
                color: AppColors.appAccent,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: onOpenGoogleMaps,
            style: OutlinedButton.styleFrom(
              foregroundColor: AppColors.appAccent,
              side: const BorderSide(color: AppColors.appAccent),
            ),
            icon: const Icon(Icons.alt_route_rounded, size: 20),
            label: const Text('Ver ruta en Google Maps'),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              if (currentStatus == 'assigned')
                FilledButton(
                  onPressed: isUpdatingStatus ? null : onMarkOnTheWay,
                  child: const Text('En camino'),
                ),
              if (currentStatus == 'on_the_way')
                FilledButton(
                  onPressed: isUpdatingStatus ? null : onMarkArrived,
                  child: const Text('Llegue'),
                ),
              if (currentStatus == 'arrived')
                FilledButton(
                  onPressed: isUpdatingStatus ? null : onMarkCompleted,
                  child: const Text('Completar'),
                ),
              if (currentStatus == 'assigned' ||
                  currentStatus == 'on_the_way' ||
                  currentStatus == 'arrived')
                OutlinedButton(
                  onPressed: isUpdatingStatus ? null : onCancel,
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFFE38A8A),
                  ),
                  child: const Text('Cancelar'),
                ),
            ],
          ),
        ],
      ),
    );
  }

  String _currentStatus() {
    final realtimeStatus = (realtimeSnapshot?.status ?? '').trim();
    if (realtimeStatus.isNotEmpty) return realtimeStatus;
    return assignment.incident.status;
  }

  String _statusLabel(String status) {
    switch (status) {
      case 'assigned':
        return 'Asignado';
      case 'on_the_way':
        return 'En camino';
      case 'arrived':
        return 'En sitio';
      case 'completed':
        return 'Completado';
      case 'cancelled':
        return 'Cancelado';
      default:
        return status;
    }
  }

  String _vehicleText() {
    final vehicle = assignment.incident.vehicle;
    if (vehicle == null) return 'Vehiculo: sin informacion';

    return 'Vehiculo: ${vehicle.make} ${vehicle.model} - ${vehicle.plate} - ${vehicle.color}';
  }
}
