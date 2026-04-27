import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/assignments/domain/domain.dart';

class MechanicActiveServiceCard extends StatelessWidget {
  const MechanicActiveServiceCard({
    super.key,
    required this.assignment,
    required this.activeSince,
    required this.isLoading,
    required this.isRefreshing,
    required this.isSyncingLocation,
    required this.locationSyncAt,
    required this.onRefresh,
    required this.onOpenService,
  });

  final MechanicAssignment? assignment;
  final DateTime? activeSince;
  final bool isLoading;
  final bool isRefreshing;
  final bool isSyncingLocation;
  final DateTime? locationSyncAt;
  final Future<void> Function() onRefresh;
  final VoidCallback onOpenService;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: AppColors.appBgMid,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                'SERVICIO ACTIVO',
                style: textTheme.titleSmall?.copyWith(
                  color: AppColors.appAccent,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const Spacer(),
              IconButton(
                onPressed: isLoading || isRefreshing ? null : onRefresh,
                icon: const Icon(Icons.refresh_rounded),
                color: AppColors.appAccent,
                tooltip: 'Actualizar',
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (isLoading)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 20),
              child: Center(
                child: CircularProgressIndicator(color: AppColors.appAccent),
              ),
            )
          else
            _AssignmentSummary(
              assignment: assignment,
              activeSince: activeSince,
              isSyncingLocation: isSyncingLocation,
              locationSyncAt: locationSyncAt,
              onOpenService: onOpenService,
            ),
        ],
      ),
    );
  }
}

class _AssignmentSummary extends StatelessWidget {
  const _AssignmentSummary({
    required this.assignment,
    required this.activeSince,
    required this.isSyncingLocation,
    required this.locationSyncAt,
    required this.onOpenService,
  });

  final MechanicAssignment? assignment;
  final DateTime? activeSince;
  final bool isSyncingLocation;
  final DateTime? locationSyncAt;
  final VoidCallback onOpenService;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    if (assignment == null) {
      return Text(
        'No tienes ningun servicio activo en este momento.',
        style: textTheme.bodyMedium?.copyWith(
          color: AppColors.appTextOnDarkMuted,
        ),
      );
    }

    final statusLabel = _statusLabel(assignment!.incident.status);

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onOpenService,
        borderRadius: BorderRadius.circular(14),
        child: Ink(
          decoration: BoxDecoration(
            color: AppColors.appBgDeep,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: AppColors.appNavBorder),
          ),
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                assignment!.incident.problemName ?? 'Servicio en curso',
                style: textTheme.bodyMedium?.copyWith(
                  color: AppColors.appTextOnDark,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Estado: $statusLabel',
                style: textTheme.bodySmall?.copyWith(
                  color: AppColors.appTextOnDarkMuted,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                'Activo hace: ${_activeSinceText(activeSince)}',
                style: textTheme.bodySmall?.copyWith(
                  color: AppColors.appAccent,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                isSyncingLocation
                    ? 'Ubicacion: sincronizando...'
                    : 'Ultimo sync: ${_syncText(locationSyncAt)}',
                style: textTheme.bodySmall?.copyWith(
                  color: AppColors.appTextOnDarkMuted,
                ),
              ),
              const SizedBox(height: 10),
              const Row(
                children: [
                  Icon(
                    Icons.route_rounded,
                    color: AppColors.appAccent,
                    size: 18,
                  ),
                  SizedBox(width: 6),
                  Text(
                    'Abrir monitoreo del servicio',
                    style: TextStyle(
                      color: AppColors.appAccent,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
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

  String _activeSinceText(DateTime? activeSince) {
    if (activeSince == null) return '--';
    final diff = DateTime.now().difference(activeSince);
    if (diff.inMinutes < 1) return 'menos de 1 min';
    if (diff.inHours < 1) return '${diff.inMinutes} min';
    return '${diff.inHours}h ${diff.inMinutes % 60}m';
  }

  String _syncText(DateTime? syncAt) {
    if (syncAt == null) return 'sin datos';
    final h = syncAt.hour.toString().padLeft(2, '0');
    final m = syncAt.minute.toString().padLeft(2, '0');
    final s = syncAt.second.toString().padLeft(2, '0');
    return '$h:$m:$s';
  }
}
