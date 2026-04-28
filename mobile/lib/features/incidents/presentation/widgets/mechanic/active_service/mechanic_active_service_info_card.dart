import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/assignments/domain/domain.dart';
import 'package:mobile/features/realtime/domain/domain.dart';

import 'mechanic_service_info_cards.dart';

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
    required this.onCallClient,
    required this.onWhatsAppClient,
  });

  final MechanicAssignment assignment;
  final IncidentRealtimeSnapshot? realtimeSnapshot;
  final bool isUpdatingStatus;
  final Future<void> Function() onMarkOnTheWay;
  final Future<void> Function() onMarkArrived;
  final Future<void> Function() onMarkCompleted;
  final Future<void> Function() onCancel;
  final Future<void> Function() onOpenGoogleMaps;
  final Future<void> Function() onCallClient;
  final Future<void> Function() onWhatsAppClient;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final currentStatus = _currentStatus();
    final statusLabel = _statusLabel(currentStatus);

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
          Row(
            children: [
              Expanded(
                child: Text(
                  assignment.incident.problemName ?? 'Servicio en curso',
                  style: textTheme.titleSmall?.copyWith(
                    color: AppColors.appTextOnDark,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              MechanicStatusChip(label: statusLabel),
            ],
          ),
          const SizedBox(height: 12),
          MechanicIncidentInfoCard(
            assignment: assignment,
            statusLabel: statusLabel,
          ),
          if (assignment.incident.evidenceUrls.isNotEmpty) ...[
            const SizedBox(height: 10),
            MechanicIncidentEvidenceSectionCard(
              evidenceUrls: assignment.incident.evidenceUrls,
            ),
          ],
          const SizedBox(height: 10),
          MechanicClientInfoCard(
            assignment: assignment,
            onCallClient: onCallClient,
            onWhatsAppClient: onWhatsAppClient,
          ),
          const SizedBox(height: 10),
          MechanicVehicleInfoCard(assignment: assignment),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: onOpenGoogleMaps,
              style: OutlinedButton.styleFrom(
                foregroundColor: AppColors.appAccent,
                side: const BorderSide(color: AppColors.appAccent),
              ),
              icon: const Icon(Icons.alt_route_rounded, size: 20),
              label: const Text('Ver ruta en Google Maps'),
            ),
          ),
          const SizedBox(height: 12),
          if (currentStatus == 'assigned' ||
              currentStatus == 'on_the_way' ||
              currentStatus == 'arrived')
            Row(
              children: [
                Expanded(
                  child: FilledButton(
                    onPressed: isUpdatingStatus
                        ? null
                        : currentStatus == 'assigned'
                        ? onMarkOnTheWay
                        : currentStatus == 'on_the_way'
                        ? onMarkArrived
                        : onMarkCompleted,
                    child: Text(
                      currentStatus == 'assigned'
                          ? 'En camino'
                          : currentStatus == 'on_the_way'
                          ? 'Llegue'
                          : 'Completar',
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: OutlinedButton(
                    onPressed: isUpdatingStatus ? null : onCancel,
                    style: OutlinedButton.styleFrom(
                      foregroundColor: const Color(0xFFE38A8A),
                    ),
                    child: const Text('Cancelar'),
                  ),
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
}
