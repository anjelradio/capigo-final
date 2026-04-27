import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:mobile/config/theme/app_theme.dart';

class MechanicActiveServiceMapSection extends StatefulWidget {
  const MechanicActiveServiceMapSection({
    super.key,
    required this.incidentLatitude,
    required this.incidentLongitude,
    this.shopLatitude,
    this.shopLongitude,
    this.mechanicLatitude,
    this.mechanicLongitude,
  });

  final double incidentLatitude;
  final double incidentLongitude;
  final double? shopLatitude;
  final double? shopLongitude;
  final double? mechanicLatitude;
  final double? mechanicLongitude;

  @override
  State<MechanicActiveServiceMapSection> createState() =>
      _MechanicActiveServiceMapSectionState();
}

class _MechanicActiveServiceMapSectionState
    extends State<MechanicActiveServiceMapSection> {
  late final MapController _mapController;
  late LatLng _initialCenter;
  static const _initialZoom = 15.0;

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
    _initialCenter = LatLng(widget.incidentLatitude, widget.incidentLongitude);
  }

  @override
  void didUpdateWidget(covariant MechanicActiveServiceMapSection oldWidget) {
    super.didUpdateWidget(oldWidget);
    final incidentChanged =
        oldWidget.incidentLatitude != widget.incidentLatitude ||
        oldWidget.incidentLongitude != widget.incidentLongitude;
    if (!incidentChanged) return;

    final center = LatLng(widget.incidentLatitude, widget.incidentLongitude);
    _initialCenter = center;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      final currentZoom = _mapController.camera.zoom;
      final targetZoom = currentZoom.isFinite ? currentZoom : _initialZoom;
      _mapController.move(center, targetZoom);
    });
  }

  @override
  Widget build(BuildContext context) {
    final incidentPoint = LatLng(
      widget.incidentLatitude,
      widget.incidentLongitude,
    );

    return FlutterMap(
      mapController: _mapController,
      options: MapOptions(
        initialCenter: _initialCenter,
        initialZoom: _initialZoom,
        interactionOptions: const InteractionOptions(
          flags: InteractiveFlag.all & ~InteractiveFlag.rotate,
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
        MarkerLayer(markers: _buildMarkers(incidentPoint)),
      ],
    );
  }

  List<Marker> _buildMarkers(LatLng incidentPoint) {
    final markers = <Marker>[
      Marker(
        point: incidentPoint,
        width: 44,
        height: 44,
        child: const Icon(
          Icons.location_on_rounded,
          color: AppColors.appAccent,
          size: 36,
        ),
      ),
    ];

    final mechanicLat = widget.mechanicLatitude;
    final mechanicLng = widget.mechanicLongitude;
    if (mechanicLat != null && mechanicLng != null) {
      markers.add(
        Marker(
          point: LatLng(mechanicLat, mechanicLng),
          width: 42,
          height: 42,
          child: const Icon(
            Icons.build_circle_rounded,
            color: Color(0xFF54B986),
            size: 32,
          ),
        ),
      );
    }

    final shopLat = widget.shopLatitude;
    final shopLng = widget.shopLongitude;
    if (shopLat != null && shopLng != null) {
      markers.add(
        Marker(
          point: LatLng(shopLat, shopLng),
          width: 40,
          height: 40,
          child: const Icon(
            Icons.garage_rounded,
            color: Color(0xFF6B7E98),
            size: 28,
          ),
        ),
      );
    }

    return markers;
  }
}
