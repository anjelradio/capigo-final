import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/incidents/presentation/providers/providers.dart';
import 'package:mobile/features/incidents/presentation/widgets/widgets.dart';
import 'package:mobile/features/realtime/realtime.dart';

class ActiveServiceScreen extends ConsumerStatefulWidget {
  const ActiveServiceScreen({super.key});

  @override
  ConsumerState<ActiveServiceScreen> createState() =>
      _ActiveServiceScreenState();
}

class _ActiveServiceScreenState extends ConsumerState<ActiveServiceScreen> {
  static const _fallbackLatitude = 13.6929;
  static const _fallbackLongitude = -89.2182;
  static const _sheetInitialSize = 0.37;
  String? _connectedIncidentId;
  final DraggableScrollableController _sheetController =
      DraggableScrollableController();

  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(activeServiceProvider.notifier).loadActiveIncident();
    });
  }

  @override
  void dispose() {
    _sheetController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screenHeight = MediaQuery.sizeOf(context).height;
    final activeState = ref.watch(activeServiceProvider);
    final activeNotifier = ref.read(activeServiceProvider.notifier);
    final detail = activeState.detail;
    final realtimeState = ref.watch(incidentRealtimeProvider);
    final mechanicLatitude = realtimeState.snapshot?.mechanicLatitude;
    final mechanicLongitude = realtimeState.snapshot?.mechanicLongitude;

    if (detail != null) {
      final incidentId = detail.incident.id;
      if (_connectedIncidentId != incidentId) {
        _connectedIncidentId = incidentId;
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (!mounted) return;
          ref
              .read(incidentRealtimeProvider.notifier)
              .connect(
                incidentId: incidentId,
                initialStatus: detail.incident.status,
              );
        });
      }
    } else if (_connectedIncidentId != null) {
      _connectedIncidentId = null;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!mounted) return;
        ref.read(incidentRealtimeProvider.notifier).disconnect();
      });
    }

    final latitude = detail?.incident.latitude ?? _fallbackLatitude;
    final longitude = detail?.incident.longitude ?? _fallbackLongitude;
    final shopLatitude = detail?.assignment?.repairShopLatitude;
    final shopLongitude = detail?.assignment?.repairShopLongitude;
    final maxSheetSize = ((screenHeight - 170) / screenHeight).clamp(
      0.62,
      0.78,
    );

    return Scaffold(
      backgroundColor: AppColors.appBgBase,
      body: Stack(
        children: [
          Positioned.fill(
            child: ActiveServiceMapSection(
              latitude: latitude,
              longitude: longitude,
              shopLatitude: shopLatitude,
              shopLongitude: shopLongitude,
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
                      AppColors.appBgDeep.withValues(alpha: 0.34),
                      AppColors.appBgDeep.withValues(alpha: 0.14),
                      Colors.transparent,
                    ],
                    stops: const [0.0, 0.16, 0.38],
                  ),
                ),
              ),
            ),
          ),
          SafeArea(
            child: _ActiveServiceHeader(
              onBackTap: () => context.go('/home/client'),
              onRefreshTap: activeState.isLoading || activeState.isRefreshing
                  ? null
                  : activeNotifier.refreshActiveIncident,
            ),
          ),
          DraggableScrollableSheet(
            controller: _sheetController,
            initialChildSize: _sheetInitialSize,
            minChildSize: _sheetInitialSize,
            maxChildSize: maxSheetSize,
            builder: (context, scrollController) {
              return Container(
                width: double.infinity,
                decoration: const BoxDecoration(
                  color: AppColors.appBgBase,
                  borderRadius: BorderRadius.only(
                    topLeft: Radius.circular(28),
                    topRight: Radius.circular(28),
                  ),
                ),
                child: SingleChildScrollView(
                  controller: scrollController,
                  physics: const ClampingScrollPhysics(),
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Center(
                          child: InkWell(
                            borderRadius: BorderRadius.circular(999),
                            onTap: () {
                              _sheetController.animateTo(
                                maxSheetSize,
                                duration: const Duration(milliseconds: 280),
                                curve: Curves.easeOutCubic,
                              );
                            },
                            child: Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 8,
                              ),
                              child: Container(
                                width: 42,
                                height: 4,
                                decoration: BoxDecoration(
                                  color: AppColors.appNavBorder,
                                  borderRadius: BorderRadius.circular(999),
                                ),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(height: 12),
                        const Text(
                          'SERVICIO EN CURSO',
                          style: TextStyle(
                            color: AppColors.appAccent,
                            fontWeight: FontWeight.w800,
                            fontSize: 16,
                          ),
                        ),
                        const SizedBox(height: 12),
                        if (activeState.isLoading && detail == null)
                          const _LoadingCard()
                        else if (detail == null)
                          _EmptyActiveServiceCard(
                            errorMessage: activeState.errorMessage,
                            onRetryTap: activeNotifier.refreshActiveIncident,
                          )
                        else
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              ActiveServiceRealtimeStatusBanner(
                                status: realtimeState.currentStatus.isNotEmpty
                                    ? realtimeState.currentStatus
                                    : detail.incident.status,
                                isConnecting: realtimeState.isConnecting,
                                isConnected: realtimeState.isConnected,
                              ),
                              const SizedBox(height: 12),
                              ActiveServiceDetailsSection(detail: detail),
                            ],
                          ),
                        const SizedBox(height: 24),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}

class _ActiveServiceHeader extends StatelessWidget {
  const _ActiveServiceHeader({
    required this.onBackTap,
    required this.onRefreshTap,
  });

  final VoidCallback onBackTap;
  final VoidCallback? onRefreshTap;

  @override
  Widget build(BuildContext context) {
    const logoPath = 'assets/images/logo/logo_header.png';
    final textTheme = Theme.of(context).textTheme;

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 10),
      child: Row(
        children: [
          IconButton(
            onPressed: onBackTap,
            style: IconButton.styleFrom(
              backgroundColor: AppColors.appBgDeep.withValues(alpha: 0.88),
              foregroundColor: AppColors.appTextOnDark,
              side: const BorderSide(color: AppColors.appNavBorder),
            ),
            icon: const Icon(Icons.arrow_back_rounded, size: 26),
            splashRadius: 22,
            tooltip: 'Volver',
          ),
          const SizedBox(width: 6),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(
              color: AppColors.appBgBase,
              borderRadius: BorderRadius.circular(999),
              border: Border.all(color: AppColors.appNavBorder),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Image.asset(
                  logoPath,
                  height: 30,
                  width: 30,
                  fit: BoxFit.contain,
                  semanticLabel: 'CapiGO',
                  errorBuilder: (_, _, _) => const Icon(
                    Icons.hexagon_rounded,
                    color: AppColors.appAccent,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 8),
                RichText(
                  text: TextSpan(
                    style: textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.2,
                    ),
                    children: const [
                      TextSpan(
                        text: 'CAPI',
                        style: TextStyle(color: AppColors.appAccent),
                      ),
                      TextSpan(
                        text: 'GO',
                        style: TextStyle(color: AppColors.appTextOnDark),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const Spacer(),
          IconButton(
            onPressed: onRefreshTap,
            style: IconButton.styleFrom(
              backgroundColor: AppColors.appBgDeep.withValues(alpha: 0.88),
              foregroundColor: AppColors.appTextOnDark,
              side: const BorderSide(color: AppColors.appNavBorder),
            ),
            icon: const Icon(Icons.refresh_rounded, size: 24),
            splashRadius: 22,
            tooltip: 'Actualizar',
          ),
        ],
      ),
    );
  }
}

class _LoadingCard extends StatelessWidget {
  const _LoadingCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.appBgMid,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      padding: const EdgeInsets.all(18),
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

class _EmptyActiveServiceCard extends StatelessWidget {
  const _EmptyActiveServiceCard({
    required this.errorMessage,
    required this.onRetryTap,
  });

  final String errorMessage;
  final VoidCallback onRetryTap;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.appBgMid,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      padding: const EdgeInsets.all(18),
      child: Column(
        children: [
          const Icon(
            Icons.design_services_rounded,
            color: AppColors.appAccent,
            size: 34,
          ),
          const SizedBox(height: 10),
          const Text(
            'No hay servicios activos',
            style: TextStyle(
              color: AppColors.appTextOnDark,
              fontWeight: FontWeight.w700,
              fontSize: 16,
            ),
          ),
          if (errorMessage.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              errorMessage,
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: AppColors.appTextOnDarkMuted,
                fontSize: 12,
              ),
            ),
          ],
          const SizedBox(height: 10),
          TextButton(
            onPressed: onRetryTap,
            child: const Text(
              'Reintentar',
              style: TextStyle(
                color: AppColors.appAccent,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
