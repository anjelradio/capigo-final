import 'package:flutter_riverpod/legacy.dart';
import 'package:geolocator/geolocator.dart';

final deviceLocationProvider =
    StateNotifierProvider<DeviceLocationNotifier, DeviceLocationState>((ref) {
      return DeviceLocationNotifier();
    });

class DeviceLocationNotifier extends StateNotifier<DeviceLocationState> {
  DeviceLocationNotifier() : super(DeviceLocationState());

  Future<void> loadCurrentLocation() async {
    if (state.isLoading || state.isRefreshing) return;
    await _resolveCurrentLocation(isRefresh: false);
  }

  Future<void> refreshLocation() async {
    if (state.isLoading || state.isRefreshing) return;
    await _resolveCurrentLocation(isRefresh: true);
  }

  Future<void> _resolveCurrentLocation({required bool isRefresh}) async {
    state = state.copyWith(
      isLoading: isRefresh ? state.isLoading : true,
      isRefreshing: isRefresh,
      errorMessages: const [],
    );

    try {
      final hasPermission = await _ensurePermission();
      if (!hasPermission) {
        if (!mounted) return;
        state = state.copyWith(
          isLoading: false,
          isRefreshing: false,
          hasLoaded: true,
          errorMessages: const ['Permiso de ubicacion denegado.'],
        );
        return;
      }

      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
        ),
      );

      if (!mounted) return;
      state = state.copyWith(
        isLoading: false,
        isRefreshing: false,
        hasLoaded: true,
        latitude: position.latitude,
        longitude: position.longitude,
        updatedAt: DateTime.now(),
        errorMessages: const [],
      );
    } catch (_) {
      if (!mounted) return;
      state = state.copyWith(
        isLoading: false,
        isRefreshing: false,
        hasLoaded: true,
        errorMessages: const ['No fue posible obtener la ubicacion actual.'],
      );
    }
  }

  Future<bool> _ensurePermission() async {
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      if (!mounted) return false;
      state = state.copyWith(
        isLoading: false,
        isRefreshing: false,
        hasLoaded: true,
        errorMessages: const ['Activa el GPS para obtener tu ubicacion.'],
      );
      return false;
    }

    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }

    if (permission == LocationPermission.denied ||
        permission == LocationPermission.deniedForever) {
      return false;
    }

    return true;
  }
}

class DeviceLocationState {
  DeviceLocationState({
    this.isLoading = false,
    this.isRefreshing = false,
    this.hasLoaded = false,
    this.latitude,
    this.longitude,
    this.updatedAt,
    this.errorMessages = const [],
  });

  final bool isLoading;
  final bool isRefreshing;
  final bool hasLoaded;
  final double? latitude;
  final double? longitude;
  final DateTime? updatedAt;
  final List<String> errorMessages;

  bool get hasLocation => latitude != null && longitude != null;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  DeviceLocationState copyWith({
    bool? isLoading,
    bool? isRefreshing,
    bool? hasLoaded,
    double? latitude,
    double? longitude,
    DateTime? updatedAt,
    List<String>? errorMessages,
  }) {
    return DeviceLocationState(
      isLoading: isLoading ?? this.isLoading,
      isRefreshing: isRefreshing ?? this.isRefreshing,
      hasLoaded: hasLoaded ?? this.hasLoaded,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      updatedAt: updatedAt ?? this.updatedAt,
      errorMessages: errorMessages ?? this.errorMessages,
    );
  }
}
