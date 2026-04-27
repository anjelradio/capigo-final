import 'package:dio/dio.dart';
import 'package:flutter_riverpod/legacy.dart';
import 'package:mobile/features/user/data/data.dart';
import 'package:mobile/features/user/domain/domain.dart';
import 'package:mobile/features/user/presentation/providers/vehicle/vehicle_repository_provider.dart';

final vehiclesProvider = StateNotifierProvider<VehiclesNotifier, VehiclesState>(
  (ref) {
    final vehicleRepository = ref.watch(vehicleRepositoryProvider);
    return VehiclesNotifier(vehicleRepository: vehicleRepository);
  },
);

class VehiclesNotifier extends StateNotifier<VehiclesState> {
  final VehicleRepository vehicleRepository;

  VehiclesNotifier({required this.vehicleRepository}) : super(VehiclesState());

  Future<void> loadVehicles() async {
    if (state.isLoading) return;

    state = state.copyWith(isLoading: true, errorMessages: const []);

    try {
      final vehicles = await vehicleRepository.getMyVehicles();
      state = state.copyWith(
        isLoading: false,
        hasLoaded: true,
        vehicles: vehicles,
        errorMessages: const [],
      );
    } on DioException catch (error) {
      state = state.copyWith(
        isLoading: false,
        hasLoaded: true,
        errorMessages: [_resolveDioError(error)],
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        hasLoaded: true,
        errorMessages: const ['Error de conexion. Intentalo nuevamente.'],
      );
    }
  }

  String _resolveDioError(DioException error) {
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.connectionError ||
        error.type == DioExceptionType.receiveTimeout) {
      return 'Error de conexion. Intentalo nuevamente.';
    }

    return 'No fue posible cargar tus vehiculos.';
  }

  void addOrUpdateVehicle(Vehicle vehicle) {
    final currentVehicles = [...state.vehicles];
    final vehicleIndex = currentVehicles.indexWhere(
      (item) => item.id == vehicle.id,
    );

    if (vehicleIndex >= 0) {
      currentVehicles[vehicleIndex] = vehicle;
    } else {
      currentVehicles.insert(0, vehicle);
    }

    state = state.copyWith(
      vehicles: currentVehicles,
      hasLoaded: true,
      errorMessages: const [],
    );
  }

  void removeVehicle(String vehicleId) {
    final currentVehicles = state.vehicles
        .where((vehicle) => vehicle.id != vehicleId)
        .toList();

    state = state.copyWith(
      vehicles: currentVehicles,
      hasLoaded: true,
      errorMessages: const [],
    );
  }
}

class VehiclesState {
  final bool isLoading;
  final bool hasLoaded;
  final List<Vehicle> vehicles;
  final List<String> errorMessages;

  VehiclesState({
    this.isLoading = false,
    this.hasLoaded = false,
    this.vehicles = const [],
    this.errorMessages = const [],
  });

  VehiclesState copyWith({
    bool? isLoading,
    bool? hasLoaded,
    List<Vehicle>? vehicles,
    List<String>? errorMessages,
  }) => VehiclesState(
    isLoading: isLoading ?? this.isLoading,
    hasLoaded: hasLoaded ?? this.hasLoaded,
    vehicles: vehicles ?? this.vehicles,
    errorMessages: errorMessages ?? this.errorMessages,
  );
}
