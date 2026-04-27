import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/shared/shared.dart';
import 'package:mobile/features/user/user.dart';

class VehicleScreen extends ConsumerWidget {
  final String vehicleId;
  final bool shouldCloseVehiclesSheetOnDelete;

  const VehicleScreen({
    super.key,
    required this.vehicleId,
    this.shouldCloseVehiclesSheetOnDelete = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final vehicleState = ref.watch(vehicleProvider(vehicleId));
    final vehicleTypesState = ref.watch(vehicleTypesProvider);
    final isCreating = vehicleId == 'new';
    final title = isCreating ? 'Crear vehiculo' : 'Editar vehiculo';

    if (vehicleState.isLoading) {
      return Scaffold(
        appBar: AppBar(title: Text(title)),
        body: const FullScreenLoader(),
      );
    }

    if (!isCreating && vehicleState.vehicle == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Editar vehiculo')),
        body: const Center(
          child: Text('No se encontro el vehiculo solicitado'),
        ),
      );
    }

    final vehicle = vehicleState.vehicle!;
    final formState = ref.watch(vehicleFormProvider(vehicle));
    final formNotifier = ref.read(vehicleFormProvider(vehicle).notifier);

    Future<void> handleSave() async {
      final wasSaved = await formNotifier.onFormSubmit();
      if (!context.mounted || !wasSaved) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            isCreating
                ? 'Vehiculo creado correctamente'
                : 'Vehiculo actualizado correctamente',
          ),
          backgroundColor: AppColors.toastSuccess,
        ),
      );

      if (isCreating) {
        Navigator.of(context).pop();
      }
    }

    Future<void> handleDelete() async {
      final confirmed = await showDialog<bool>(
        context: context,
        builder: (_) => const AppConfirmDialog(
          title: 'Eliminar vehiculo',
          description:
              'Esta accion eliminara el vehiculo de tu cuenta. ¿Deseas continuar?',
          confirmText: 'Si, eliminar',
        ),
      );

      if (!context.mounted || confirmed != true) return;

      final wasDeleted = await formNotifier.onDeleteVehicle();
      if (!context.mounted || !wasDeleted) return;

      final navigator = Navigator.of(context);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Vehiculo eliminado correctamente'),
          backgroundColor: AppColors.toastSuccess,
        ),
      );

      navigator.pop();
      if (shouldCloseVehiclesSheetOnDelete && navigator.canPop()) {
        navigator.pop();
      }
    }

    return Scaffold(
      appBar: VehicleScreenAppBar(
        title: title,
        showDeleteAction: !isCreating,
        isPosting: formState.isPosting,
        onDeletePressed: handleDelete,
      ),
      floatingActionButton: isCreating
          ? null
          : VehicleSaveFab(isPosting: formState.isPosting, onSave: handleSave),
      bottomNavigationBar: isCreating
          ? VehicleCreateBottomBar(
              isPosting: formState.isPosting,
              onSave: handleSave,
            )
          : null,
      body: SingleChildScrollView(
        padding: EdgeInsets.fromLTRB(16, 16, 16, isCreating ? 20 : 120),
        child: VehicleFormSection(
          formState: formState,
          formNotifier: formNotifier,
          vehicleTypesState: vehicleTypesState,
        ),
      ),
    );
  }
}
