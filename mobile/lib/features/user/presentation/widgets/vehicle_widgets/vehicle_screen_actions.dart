import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/shared/shared.dart';

class VehicleSaveFab extends StatelessWidget {
  const VehicleSaveFab({
    super.key,
    required this.isPosting,
    required this.onSave,
  });

  final bool isPosting;
  final VoidCallback onSave;

  @override
  Widget build(BuildContext context) {
    return FloatingActionButton.extended(
      backgroundColor: AppColors.appAccent,
      foregroundColor: AppColors.appAccentText,
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(22)),
      onPressed: isPosting ? null : onSave,
      icon: isPosting
          ? const SizedBox(
              width: 18,
              height: 18,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: AppColors.appAccentText,
              ),
            )
          : const Icon(Icons.save_outlined),
      label: Text(isPosting ? 'Guardando...' : 'Guardar'),
    );
  }
}

class VehicleCreateBottomBar extends StatelessWidget {
  const VehicleCreateBottomBar({
    super.key,
    required this.isPosting,
    required this.onSave,
  });

  final bool isPosting;
  final VoidCallback onSave;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      minimum: const EdgeInsets.fromLTRB(16, 8, 16, 12),
      child: SizedBox(
        height: 52,
        child: CustomFilledButton(
          text: isPosting ? 'Guardando...' : 'Crear vehiculo',
          onPressed: isPosting ? null : onSave,
        ),
      ),
    );
  }
}
