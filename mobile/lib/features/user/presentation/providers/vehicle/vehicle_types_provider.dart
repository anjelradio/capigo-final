import 'package:dio/dio.dart';
import 'package:flutter_riverpod/legacy.dart';
import 'package:mobile/features/auth/data/errors/auth_errors.dart';
import 'package:mobile/features/user/data/data.dart';
import 'package:mobile/features/user/domain/domain.dart';
import 'package:mobile/features/user/presentation/providers/vehicle/vehicle_repository_provider.dart';

final vehicleTypesProvider =
    StateNotifierProvider<VehicleTypesNotifier, VehicleTypesState>((ref) {
      final vehicleRepository = ref.watch(vehicleRepositoryProvider);
      return VehicleTypesNotifier(vehicleRepository: vehicleRepository);
    });

class VehicleTypesNotifier extends StateNotifier<VehicleTypesState> {
  VehicleTypesNotifier({required this.vehicleRepository})
    : super(VehicleTypesState()) {
    loadVehicleTypes();
  }

  final VehicleRepository vehicleRepository;

  Future<void> loadVehicleTypes() async {
    if (state.isLoading) return;

    state = state.copyWith(isLoading: true, errorMessages: const []);

    try {
      final vehicleTypes = await vehicleRepository.getVehicleTypes();
      state = state.copyWith(
        isLoading: false,
        hasLoaded: true,
        vehicleTypes: vehicleTypes,
        errorMessages: const [],
      );
    } on CustomError catch (e) {
      state = state.copyWith(
        isLoading: false,
        hasLoaded: true,
        errorMessages: e.messages,
      );
    } on DioException catch (_) {
      state = state.copyWith(
        isLoading: false,
        hasLoaded: true,
        errorMessages: const ['No fue posible cargar los tipos de vehiculo.'],
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        hasLoaded: true,
        errorMessages: const ['No fue posible cargar los tipos de vehiculo.'],
      );
    }
  }
}

class VehicleTypesState {
  VehicleTypesState({
    this.isLoading = false,
    this.hasLoaded = false,
    this.vehicleTypes = const [],
    this.errorMessages = const [],
  });

  final bool isLoading;
  final bool hasLoaded;
  final List<VehicleType> vehicleTypes;
  final List<String> errorMessages;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  VehicleTypesState copyWith({
    bool? isLoading,
    bool? hasLoaded,
    List<VehicleType>? vehicleTypes,
    List<String>? errorMessages,
  }) => VehicleTypesState(
    isLoading: isLoading ?? this.isLoading,
    hasLoaded: hasLoaded ?? this.hasLoaded,
    vehicleTypes: vehicleTypes ?? this.vehicleTypes,
    errorMessages: errorMessages ?? this.errorMessages,
  );
}
