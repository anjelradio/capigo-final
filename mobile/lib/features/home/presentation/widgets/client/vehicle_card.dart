import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/user/domain/domain.dart';

class VehicleCard extends StatelessWidget {
  const VehicleCard({required this.vehicle, required this.onTap, super.key});

  final Vehicle vehicle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(24),
        onTap: onTap,
        child: Ink(
          decoration: BoxDecoration(
            color: AppColors.appBgMid,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: AppColors.appNavBorder),
          ),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(
              children: [
                _VehicleTypeBadge(typeName: vehicle.type.name),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${vehicle.make} ${vehicle.model}',
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: AppColors.appAccent,
                          fontSize: 16,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Placa: ${vehicle.plate}',
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: AppColors.appTextOnDark,
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'Modelo: ${vehicle.model}',
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: AppColors.appTextOnDarkMuted,
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _VehicleTypeBadge extends StatelessWidget {
  const _VehicleTypeBadge({required this.typeName});

  final String typeName;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 60,
      height: 60,
      decoration: BoxDecoration(
        color: AppColors.appBgDeep,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      alignment: Alignment.center,
      child: Transform.translate(
        offset: const Offset(-1.4, 0),
        child: Image.asset(
          _resolveImagePath(typeName),
          width: 65,
          height: 65,
          fit: BoxFit.contain,
        ),
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
