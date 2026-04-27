import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/user/presentation/providers/providers.dart';

class ClientLocationMapSection extends ConsumerStatefulWidget {
  const ClientLocationMapSection({
    super.key,
    this.height,
    this.horizontalPadding = 0,
  });

  final double? height;
  final double horizontalPadding;

  @override
  ConsumerState<ClientLocationMapSection> createState() =>
      _ClientLocationMapSectionState();
}

class _ClientLocationMapSectionState
    extends ConsumerState<ClientLocationMapSection> {
  static const _fallbackCenter = LatLng(13.6929, -89.2182);

  @override
  void initState() {
    super.initState();

    Future.microtask(() {
      final locationState = ref.read(deviceLocationProvider);
      if (!locationState.hasLoaded && !locationState.isLoading) {
        ref.read(deviceLocationProvider.notifier).loadCurrentLocation();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final locationState = ref.watch(deviceLocationProvider);
    final locationNotifier = ref.read(deviceLocationProvider.notifier);

    final isUpdating = locationState.isLoading || locationState.isRefreshing;
    final hasLocation = locationState.hasLocation;

    final center = hasLocation
        ? LatLng(locationState.latitude!, locationState.longitude!)
        : _fallbackCenter;

    final buttonText = isUpdating
        ? 'ACTUALIZANDO UBICACION...'
        : 'ACTUALIZAR UBICACION';

    return Padding(
      padding: EdgeInsets.symmetric(horizontal: widget.horizontalPadding),
      child: SizedBox(
        height: widget.height ?? 220,
        child: Stack(
          clipBehavior: Clip.none,
          children: [
            Positioned.fill(
              child: ClipRRect(
                child: hasLocation
                    ? FlutterMap(
                        options: MapOptions(
                          initialCenter: center,
                          initialZoom: 15,
                          interactionOptions: const InteractionOptions(
                            flags: InteractiveFlag.none,
                          ),
                        ),
                        children: [
                          TileLayer(
                            urlTemplate:
                                'https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
                            userAgentPackageName: 'com.capigo.mobile',
                            retinaMode: RetinaMode.isHighDensity(context),
                            maxNativeZoom: 20,
                            maxZoom: 20,
                          ),
                          MarkerLayer(
                            markers: [
                              Marker(
                                point: center,
                                width: 40,
                                height: 40,
                                child: const Icon(
                                  Icons.location_on_rounded,
                                  color: AppColors.appAccent,
                                  size: 34,
                                ),
                              ),
                            ],
                          ),
                        ],
                      )
                    : const _MapFallbackSurface(),
              ),
            ),
            if (locationState.errorMessage.isNotEmpty)
              Positioned(
                top: 16,
                left: 16,
                right: 16,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 8,
                  ),
                  decoration: BoxDecoration(
                    color: AppColors.toastWarning.withValues(alpha: 0.18),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppColors.appAccentDeep),
                  ),
                  child: Text(
                    locationState.errorMessage,
                    style: textTheme.labelSmall?.copyWith(
                      color: AppColors.appTextOnDark,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),
            Positioned(
              left: 16,
              right: 16,
              bottom: 78,
              child: Material(
                color: Colors.transparent,
                child: InkWell(
                  onTap: isUpdating ? null : locationNotifier.refreshLocation,
                  borderRadius: BorderRadius.circular(18),
                  child: Ink(
                    height: 36,
                    decoration: BoxDecoration(
                      color: AppColors.appBgDeep,
                      borderRadius: BorderRadius.circular(18),
                      border: Border.all(color: AppColors.appNavBorder),
                    ),
                    padding: const EdgeInsets.symmetric(horizontal: 10),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          isUpdating
                              ? Icons.sync_rounded
                              : Icons.my_location_rounded,
                          size: 15,
                          color: AppColors.appAccent,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          buttonText,
                          style: textTheme.labelSmall?.copyWith(
                            color: AppColors.appTextOnDark,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.2,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _MapFallbackSurface extends StatelessWidget {
  const _MapFallbackSurface();

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [AppColors.appBgMid, AppColors.appBgDeep],
        ),
      ),
      child: const _MapPlaceholderPattern(),
    );
  }
}

class _MapPlaceholderPattern extends StatelessWidget {
  const _MapPlaceholderPattern();

  @override
  Widget build(BuildContext context) {
    return CustomPaint(painter: _MapGridPainter());
  }
}

class _MapGridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = AppColors.appNavBorder
      ..strokeWidth = 1.2
      ..style = PaintingStyle.stroke;

    for (double y = 18; y < size.height; y += 24) {
      final path = ui.Path();
      path.moveTo(0, y);
      path.cubicTo(
        size.width * 0.25,
        y - 10,
        size.width * 0.5,
        y + 10,
        size.width,
        y - 2,
      );
      canvas.drawPath(path, paint);
    }

    for (double x = 16; x < size.width; x += 26) {
      final path = ui.Path();
      path.moveTo(x, 0);
      path.cubicTo(
        x - 8,
        size.height * 0.35,
        x + 10,
        size.height * 0.65,
        x - 2,
        size.height,
      );
      canvas.drawPath(path, paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return false;
  }
}
