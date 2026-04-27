import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/assignments/assignments.dart';
import 'package:mobile/features/incidents/presentation/widgets/widgets.dart';
import 'package:mobile/features/realtime/realtime.dart';
import 'package:url_launcher/url_launcher.dart';

class MechanicActiveServiceScreen extends ConsumerStatefulWidget {
  const MechanicActiveServiceScreen({super.key});

  @override
  ConsumerState<MechanicActiveServiceScreen> createState() =>
      _MechanicActiveServiceScreenState();
}

class _MechanicActiveServiceScreenState
    extends ConsumerState<MechanicActiveServiceScreen> {
  static const _fallbackLatitude = 13.6929;
  static const _fallbackLongitude = -89.2182;
  String? _connectedIncidentId;
  late final MechanicActiveAssignmentNotifier _assignmentNotifier;
  late final IncidentRealtimeNotifier _incidentRealtimeNotifier;

  @override
  void initState() {
    super.initState();
    _assignmentNotifier = ref.read(mechanicActiveAssignmentProvider.notifier);
    _incidentRealtimeNotifier = ref.read(incidentRealtimeProvider.notifier);

    Future.microtask(() async {
      await _assignmentNotifier.loadActiveAssignment();
      await _assignmentNotifier.loadAssignmentDetail();
      if (!mounted) return;
      _assignmentNotifier.startLocationSync();
    });
  }

  @override
  void dispose() {
    _assignmentNotifier.stopLocationSync();
    _incidentRealtimeNotifier.disconnect();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final assignmentState = ref.watch(mechanicActiveAssignmentProvider);
    final assignmentNotifier = _assignmentNotifier;
    final assignment = assignmentState.assignment;
    final realtimeState = ref.watch(incidentRealtimeProvider);
    final incidentId = assignment?.incident.id ?? '';

    if (incidentId.isNotEmpty) {
      if (_connectedIncidentId != incidentId) {
        _connectedIncidentId = incidentId;
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (!mounted) return;
          _incidentRealtimeNotifier.connect(
            incidentId: incidentId,
            initialStatus: assignment?.incident.status ?? '',
          );
        });
      }
    } else if (_connectedIncidentId != null) {
      _connectedIncidentId = null;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!mounted) return;
        _incidentRealtimeNotifier.disconnect();
      });
    }

    final incidentLatitude = assignment?.incident.latitude ?? _fallbackLatitude;
    final incidentLongitude =
        assignment?.incident.longitude ?? _fallbackLongitude;
    final mechanicLatitude = realtimeState.snapshot?.mechanicLatitude;
    final mechanicLongitude = realtimeState.snapshot?.mechanicLongitude;

    ref.listen(mechanicActiveAssignmentProvider, (previous, next) {
      if (next.lastActionMessage.isNotEmpty &&
          next.lastActionMessage != previous?.lastActionMessage) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(next.lastActionMessage)));
        _assignmentNotifier.clearLastActionMessage();
      }
    });

    return Scaffold(
      backgroundColor: AppColors.appBgBase,
      body: Stack(
        children: [
          Positioned.fill(
            child: MechanicActiveServiceMapSection(
              incidentLatitude: incidentLatitude,
              incidentLongitude: incidentLongitude,
              shopLatitude: assignment?.repairShopLatitude,
              shopLongitude: assignment?.repairShopLongitude,
              mechanicLatitude: mechanicLatitude,
              mechanicLongitude: mechanicLongitude,
            ),
          ),
          Positioned.fill(
            child: IgnorePointer(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      AppColors.appBgDeep.withValues(alpha: 0.32),
                      AppColors.appBgDeep.withValues(alpha: 0.16),
                      Colors.transparent,
                    ],
                    stops: const [0.0, 0.16, 0.38],
                  ),
                ),
              ),
            ),
          ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 14, 16, 10),
              child: Row(
                children: [
                  IconButton(
                    onPressed: () => context.pop(),
                    style: IconButton.styleFrom(
                      backgroundColor: AppColors.appBgDeep.withValues(
                        alpha: 0.88,
                      ),
                      foregroundColor: AppColors.appTextOnDark,
                      side: const BorderSide(color: AppColors.appNavBorder),
                    ),
                    icon: const Icon(Icons.arrow_back_rounded, size: 26),
                    tooltip: 'Volver',
                  ),
                  const Spacer(),
                  IconButton(
                    onPressed:
                        assignmentState.isLoading ||
                            assignmentState.isRefreshing
                        ? null
                        : () async {
                            await assignmentNotifier.refreshActiveAssignment();
                            await assignmentNotifier.loadAssignmentDetail();
                          },
                    style: IconButton.styleFrom(
                      backgroundColor: AppColors.appBgDeep.withValues(
                        alpha: 0.88,
                      ),
                      foregroundColor: AppColors.appTextOnDark,
                      side: const BorderSide(color: AppColors.appNavBorder),
                    ),
                    icon: const Icon(Icons.refresh_rounded, size: 24),
                    tooltip: 'Actualizar',
                  ),
                ],
              ),
            ),
          ),
          Align(
            alignment: Alignment.bottomCenter,
            child: Container(
              width: double.infinity,
              constraints: const BoxConstraints(maxHeight: 420),
              decoration: const BoxDecoration(
                color: AppColors.appBgBase,
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(28),
                  topRight: Radius.circular(28),
                ),
              ),
              child: SingleChildScrollView(
                physics: const ClampingScrollPhysics(),
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Center(
                      child: SizedBox(
                        width: 42,
                        height: 4,
                        child: DecoratedBox(
                          decoration: BoxDecoration(
                            color: AppColors.appNavBorder,
                            borderRadius: BorderRadius.all(
                              Radius.circular(999),
                            ),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    ActiveServiceRealtimeStatusBanner(
                      status: realtimeState.currentStatus.isNotEmpty
                          ? realtimeState.currentStatus
                          : (assignment?.incident.status ?? ''),
                      isConnecting: realtimeState.isConnecting,
                      isConnected: realtimeState.isConnected,
                    ),
                    const SizedBox(height: 10),
                    if (assignmentState.isLoading && assignment == null)
                      const _LoadingInfo()
                    else if (assignment == null)
                      _EmptyInfo(
                        errorMessage: assignmentState.errorMessage,
                        onRetryTap: () async {
                          await assignmentNotifier.refreshActiveAssignment();
                          await assignmentNotifier.loadAssignmentDetail();
                        },
                      )
                    else
                      MechanicActiveServiceInfoCard(
                        assignment: assignment,
                        realtimeSnapshot: realtimeState.snapshot,
                        isUpdatingStatus: assignmentState.isUpdatingStatus,
                        onMarkOnTheWay: () =>
                            assignmentNotifier.updateStatus('on_the_way'),
                        onMarkArrived: () =>
                            assignmentNotifier.updateStatus('arrived'),
                        onMarkCompleted: () =>
                            assignmentNotifier.updateStatus('completed'),
                        onCancel: () async {
                          final shouldCancel = await _confirmCancelService();
                          if (!shouldCancel) return;
                          await assignmentNotifier.updateStatus('cancelled');
                        },
                        onOpenGoogleMaps: () => _openGoogleMaps(
                          latitude: assignment.incident.latitude,
                          longitude: assignment.incident.longitude,
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _openGoogleMaps({
    required double latitude,
    required double longitude,
  }) async {
    final externalUri = Uri.parse(
      'https://www.google.com/maps/dir/?api=1&destination=$latitude,$longitude&travelmode=driving',
    );

    try {
      final launched = await launchUrl(
        externalUri,
        mode: LaunchMode.externalApplication,
      );
      if (launched) return;
    } on PlatformException {
      // Continue with fallback to avoid crashing on channel errors.
    } catch (_) {
      // Continue with fallback.
    }

    try {
      final fallbackLaunched = await launchUrl(
        externalUri,
        mode: LaunchMode.platformDefault,
      );
      if (fallbackLaunched) return;
    } on PlatformException {
      // handled below
    } catch (_) {
      // handled below
    }

    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('No se pudo abrir Google Maps en este dispositivo.'),
      ),
    );
  }

  Future<bool> _confirmCancelService() async {
    final result = await showDialog<bool>(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: const Text('Cancelar servicio'),
          content: const Text(
            'Estas seguro de que deseas cancelar este servicio?',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(false),
              child: const Text('Volver'),
            ),
            FilledButton(
              onPressed: () => Navigator.of(dialogContext).pop(true),
              child: const Text('Confirmar'),
            ),
          ],
        );
      },
    );

    return result ?? false;
  }
}

class _LoadingInfo extends StatelessWidget {
  const _LoadingInfo();

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.appBgMid,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      padding: const EdgeInsets.all(16),
      child: const Row(
        children: [
          SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(
              strokeWidth: 2.2,
              color: AppColors.appAccent,
            ),
          ),
          SizedBox(width: 10),
          Expanded(
            child: Text(
              'Cargando servicio activo...',
              style: TextStyle(
                color: AppColors.appTextOnDark,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _EmptyInfo extends StatelessWidget {
  const _EmptyInfo({required this.errorMessage, required this.onRetryTap});

  final String errorMessage;
  final Future<void> Function() onRetryTap;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.appBgMid,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          const Icon(
            Icons.construction_rounded,
            color: AppColors.appAccent,
            size: 34,
          ),
          const SizedBox(height: 10),
          Text(
            'No tienes un servicio activo ahora.',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: AppColors.appTextOnDark,
              fontWeight: FontWeight.w700,
            ),
          ),
          if (errorMessage.trim().isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              errorMessage,
              textAlign: TextAlign.center,
              style: Theme.of(
                context,
              ).textTheme.bodySmall?.copyWith(color: const Color(0xFFE38A8A)),
            ),
          ],
          const SizedBox(height: 10),
          TextButton(onPressed: onRetryTap, child: const Text('Reintentar')),
        ],
      ),
    );
  }
}
