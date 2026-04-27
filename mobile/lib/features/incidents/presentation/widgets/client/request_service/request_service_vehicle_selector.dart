import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/user/domain/domain.dart';

class RequestServiceVehicleSelector extends StatelessWidget {
  const RequestServiceVehicleSelector({
    super.key,
    required this.vehicles,
    required this.isLoading,
    required this.selectedVehicleId,
    required this.onChanged,
  });

  final List<Vehicle> vehicles;
  final bool isLoading;
  final String? selectedVehicleId;
  final ValueChanged<String?> onChanged;

  @override
  Widget build(BuildContext context) {
    final selectedVehicle = _findSelectedVehicle();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.appBgMid,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Vehiculo involucrado',
            style: TextStyle(
              color: AppColors.appAccent,
              fontWeight: FontWeight.w800,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 10),
          Material(
            color: Colors.transparent,
            child: InkWell(
              borderRadius: BorderRadius.circular(16),
              onTap: () => _openVehiclePicker(context),
              child: Ink(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 12,
                ),
                decoration: BoxDecoration(
                  color: AppColors.appBgDeep,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppColors.appAccentDeep),
                ),
                child: Row(
                  children: [
                    _VehicleTypeBadge(typeName: selectedVehicle?.type.name),
                    const SizedBox(width: 10),
                    Expanded(
                      child: isLoading
                          ? const Text(
                              'Cargando vehiculos...',
                              style: TextStyle(
                                color: AppColors.appTextOnDarkMuted,
                              ),
                            )
                          : selectedVehicle == null
                          ? const Text(
                              'Selecciona tu vehiculo',
                              style: TextStyle(
                                color: AppColors.appTextOnDarkMuted,
                              ),
                            )
                          : Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  '${selectedVehicle.make} ${selectedVehicle.model}',
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: const TextStyle(
                                    color: AppColors.appTextOnDark,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  'Placa: ${selectedVehicle.plate}',
                                  style: const TextStyle(
                                    color: AppColors.appTextOnDarkMuted,
                                    fontSize: 12,
                                  ),
                                ),
                              ],
                            ),
                    ),
                    const SizedBox(width: 8),
                    const Icon(
                      Icons.keyboard_arrow_down_rounded,
                      color: AppColors.appAccent,
                      size: 26,
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

  Vehicle? _findSelectedVehicle() {
    if (selectedVehicleId == null) return null;
    for (final vehicle in vehicles) {
      if (vehicle.id == selectedVehicleId) return vehicle;
    }
    return null;
  }

  Future<void> _openVehiclePicker(BuildContext context) async {
    final selectedId = await showModalBottomSheet<String>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (sheetContext) {
        return SafeArea(
          top: false,
          child: Container(
            height: MediaQuery.of(sheetContext).size.height * 0.72,
            decoration: const BoxDecoration(
              color: AppColors.appBgBase,
              borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
            ),
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(18, 14, 8, 8),
                  child: Row(
                    children: [
                      const Expanded(
                        child: Text(
                          'Selecciona un vehiculo',
                          style: TextStyle(
                            color: AppColors.appAccent,
                            fontWeight: FontWeight.w800,
                            fontSize: 18,
                          ),
                        ),
                      ),
                      IconButton(
                        onPressed: () => Navigator.of(sheetContext).pop(),
                        icon: const Icon(
                          Icons.close_rounded,
                          color: AppColors.appAccent,
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: isLoading
                      ? const Center(
                          child: CircularProgressIndicator(
                            color: AppColors.appAccent,
                          ),
                        )
                      : vehicles.isEmpty
                      ? const Center(
                          child: Padding(
                            padding: EdgeInsets.symmetric(horizontal: 24),
                            child: Text(
                              'No tienes vehiculos registrados aun.',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                color: AppColors.appTextOnDarkMuted,
                              ),
                            ),
                          ),
                        )
                      : ListView.separated(
                          padding: const EdgeInsets.fromLTRB(16, 8, 16, 18),
                          itemCount: vehicles.length,
                          separatorBuilder: (_, _) =>
                              const SizedBox(height: 10),
                          itemBuilder: (_, index) {
                            final vehicle = vehicles[index];
                            final isSelected = vehicle.id == selectedVehicleId;
                            return _VehiclePickerCard(
                              vehicle: vehicle,
                              isSelected: isSelected,
                              onTap: () =>
                                  Navigator.of(sheetContext).pop(vehicle.id),
                            );
                          },
                        ),
                ),
              ],
            ),
          ),
        );
      },
    );

    if (selectedId != null) {
      onChanged(selectedId);
    }
  }
}

class _VehiclePickerCard extends StatelessWidget {
  const _VehiclePickerCard({
    required this.vehicle,
    required this.isSelected,
    required this.onTap,
  });

  final Vehicle vehicle;
  final bool isSelected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: onTap,
        child: Ink(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: isSelected ? AppColors.appBgDeep : AppColors.appBgMid,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: isSelected ? AppColors.appAccent : AppColors.appNavBorder,
              width: isSelected ? 1.5 : 1,
            ),
          ),
          child: Row(
            children: [
              _VehicleTypeBadge(typeName: vehicle.type.name),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${vehicle.make} ${vehicle.model}',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: AppColors.appTextOnDark,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Placa: ${vehicle.plate}',
                      style: const TextStyle(
                        color: AppColors.appTextOnDarkMuted,
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Color: ${vehicle.color} • ${vehicle.year}',
                      style: const TextStyle(
                        color: AppColors.appTextOnDarkMuted,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              Icon(
                isSelected
                    ? Icons.radio_button_checked_rounded
                    : Icons.radio_button_unchecked_rounded,
                color: isSelected
                    ? AppColors.appAccent
                    : AppColors.appTextOnDarkMuted,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _VehicleTypeBadge extends StatelessWidget {
  const _VehicleTypeBadge({this.typeName});

  final String? typeName;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 52,
      height: 52,
      decoration: BoxDecoration(
        color: AppColors.appBgDeep,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      alignment: Alignment.center,
      child: Image.asset(
        _resolveImagePath(typeName ?? ''),
        width: 54,
        height: 54,
        fit: BoxFit.contain,
      ),
    );
  }

  String _resolveImagePath(String vehicleType) {
    switch (vehicleType.toLowerCase()) {
      case 'motorcycle':
        return 'assets/images/buttons/vehicle_types/motorcycle.png';
      case 'truck':
        return 'assets/images/buttons/vehicle_types/truck.png';
      case 'car':
      default:
        return 'assets/images/buttons/vehicle_types/car.png';
    }
  }
}
