import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/legacy.dart';
import 'package:mobile/features/user/user.dart';

final vehicleProvider = StateNotifierProvider.autoDispose
    .family<VehicleNotifier, VehicleState, String>((ref, vehicleId) {
      final vehicleRepository = ref.watch(vehicleRepositoryProvider);
      return VehicleNotifier(
        vehicleRepository: vehicleRepository,
        vehicleId: vehicleId,
      );
    });

class VehicleNotifier extends StateNotifier<VehicleState> {
  final VehicleRepository vehicleRepository;

  VehicleNotifier({required this.vehicleRepository, required String vehicleId})
    : super(VehicleState(id: vehicleId)) {
    loadVehicle();
  }

  Vehicle newEmptyVehicle() {
    return Vehicle(
      id: 'new',
      make: '',
      model: '',
      plate: '',
      color: '',
      year: 0,
      type: VehicleType(id: '', name: ''),
    );
  }

  Future<void> loadVehicle() async {
    if (state.id == 'new') {
      state = state.copyWith(isLoading: false, vehicle: newEmptyVehicle());
      return;
    }

    try {
      final vehicle = await vehicleRepository.getVehicleById(state.id);
      state = state.copyWith(isLoading: false, vehicle: vehicle);
    } catch (e) {
      debugPrint('Error loading vehicle: $e');
      state = state.copyWith(isLoading: false);
    }
  }
}

class VehicleState {
  final String id;
  final Vehicle? vehicle;
  final bool isLoading;
  final bool isSaving;

  VehicleState({
    required this.id,
    this.vehicle,
    this.isLoading = true,
    this.isSaving = false,
  });

  VehicleState copyWith({
    String? id,
    Vehicle? vehicle,
    bool? isLoading,
    bool? isSaving,
  }) => VehicleState(
    id: id ?? this.id,
    vehicle: vehicle ?? this.vehicle,
    isLoading: isLoading ?? this.isLoading,
    isSaving: isSaving ?? this.isSaving,
  );
}
