import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/shared/shared.dart';
import 'package:mobile/features/user/domain/domain.dart';
import 'package:mobile/features/user/presentation/providers/providers.dart';

class VehicleFormSection extends StatelessWidget {
  const VehicleFormSection({
    super.key,
    required this.formState,
    required this.formNotifier,
    required this.vehicleTypesState,
  });

  final VehicleFormState formState;
  final VehicleFormNotifier formNotifier;
  final VehicleTypesState vehicleTypesState;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (formState.errorMessage.isNotEmpty) ...[
          Text(
            formState.errorMessage,
            style: const TextStyle(
              color: Colors.red,
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
        ],
        if (vehicleTypesState.errorMessage.isNotEmpty) ...[
          Text(
            vehicleTypesState.errorMessage,
            style: const TextStyle(
              color: Colors.red,
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
        ],
        CustomTextFormField(
          label: 'Marca',
          initialValue: formState.make.value,
          onChanged: formNotifier.onMakeChanged,
          errorMessage: formState.isFormPosted
              ? formState.make.errorMessage
              : null,
        ),
        const SizedBox(height: 16),
        CustomTextFormField(
          label: 'Modelo',
          initialValue: formState.model.value,
          onChanged: formNotifier.onModelChanged,
          errorMessage: formState.isFormPosted
              ? formState.model.errorMessage
              : null,
        ),
        const SizedBox(height: 16),
        CustomTextFormField(
          label: 'Placa',
          initialValue: formState.plate.value,
          onChanged: formNotifier.onPlateChanged,
          errorMessage: formState.isFormPosted
              ? formState.plate.errorMessage
              : null,
        ),
        const SizedBox(height: 16),
        CustomTextFormField(
          label: 'Color',
          initialValue: formState.color.value,
          onChanged: formNotifier.onColorChanged,
          errorMessage: formState.isFormPosted
              ? formState.color.errorMessage
              : null,
        ),
        const SizedBox(height: 16),
        CustomTextFormField(
          label: 'Anio',
          initialValue: formState.year.value,
          keyboardType: TextInputType.number,
          onChanged: formNotifier.onYearChanged,
          errorMessage: formState.isFormPosted
              ? formState.year.errorMessage
              : null,
        ),
        const SizedBox(height: 24),
        const Text(
          'Tipo de vehiculo',
          style: TextStyle(
            color: AppColors.appAccent,
            fontSize: 15,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 10),
        if (vehicleTypesState.isLoading)
          const Center(child: CircularProgressIndicator())
        else
          VehicleTypeSelector(
            vehicleTypes: vehicleTypesState.vehicleTypes,
            selectedTypeId: formState.typeId.value,
            onSelect: (vehicleType) => formNotifier.onTypeChanged(
              id: vehicleType.id,
              name: vehicleType.name,
            ),
          ),
        if (formState.isFormPosted &&
            formState.typeId.errorMessage != null) ...[
          const SizedBox(height: 8),
          Text(
            formState.typeId.errorMessage!,
            style: const TextStyle(
              color: Colors.red,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ],
    );
  }
}

class VehicleTypeSelector extends StatelessWidget {
  const VehicleTypeSelector({
    super.key,
    required this.vehicleTypes,
    required this.selectedTypeId,
    required this.onSelect,
  });

  final List<VehicleType> vehicleTypes;
  final String selectedTypeId;
  final void Function(VehicleType vehicleType) onSelect;

  @override
  Widget build(BuildContext context) {
    if (vehicleTypes.isEmpty) {
      return const Text(
        'No hay tipos de vehiculo disponibles.',
        style: TextStyle(
          color: AppColors.appTextOnDarkMuted,
          fontSize: 13,
          fontWeight: FontWeight.w600,
        ),
      );
    }

    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: vehicleTypes.map((vehicleType) {
        final isSelected = selectedTypeId == vehicleType.id;
        return _VehicleTypeOption(
          vehicleType: vehicleType,
          isSelected: isSelected,
          onTap: () => onSelect(vehicleType),
        );
      }).toList(),
    );
  }
}

class _VehicleTypeOption extends StatelessWidget {
  const _VehicleTypeOption({
    required this.vehicleType,
    required this.isSelected,
    required this.onTap,
  });

  final VehicleType vehicleType;
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
          width: 110,
          padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
          decoration: BoxDecoration(
            color: isSelected ? AppColors.appBgDeep : AppColors.appBgMid,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: isSelected ? AppColors.appAccent : AppColors.appAccentDeep,
              width: isSelected ? 1.6 : 1,
            ),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              _VehicleTypeBadge(
                typeName: vehicleType.name,
                isSelected: isSelected,
              ),
              const SizedBox(height: 8),
              Text(
                _labelFromType(vehicleType.name),
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: isSelected
                      ? AppColors.appAccent
                      : AppColors.appTextOnDark,
                  fontSize: 12,
                  fontWeight: isSelected ? FontWeight.w800 : FontWeight.w700,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _labelFromType(String typeName) {
    switch (typeName.toLowerCase()) {
      case 'motorcycle':
        return 'Moto';
      case 'truck':
        return 'Camioneta';
      case 'car':
      default:
        return 'Auto';
    }
  }
}

class _VehicleTypeBadge extends StatelessWidget {
  const _VehicleTypeBadge({required this.typeName, required this.isSelected});

  final String typeName;
  final bool isSelected;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 56,
      height: 56,
      decoration: BoxDecoration(
        color: isSelected
            ? AppColors.appAccent.withValues(alpha: 0.24)
            : AppColors.appBgDeep,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isSelected ? AppColors.appAccent : AppColors.appNavBorder,
        ),
      ),
      alignment: Alignment.center,
      child: Transform.translate(
        offset: const Offset(-1.2, 0),
        child: Image.asset(
          _resolveImagePath(typeName),
          width: 60,
          height: 60,
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
