import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/features/shared/shared.dart';
import 'package:mobile/features/user/presentation/providers/providers.dart';

class ChangePasswordDialog extends ConsumerWidget {
  const ChangePasswordDialog({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final formState = ref.watch(passwordChangeFormProvider);
    final formNotifier = ref.read(passwordChangeFormProvider.notifier);

    Future<void> onSubmit() async {
      final isSuccess = await formNotifier.submit();
      if (!context.mounted) return;

      if (isSuccess) {
        Navigator.of(context).pop(true);
        return;
      }

      final message = ref.read(passwordChangeFormProvider).errorMessage;
      if (message.isEmpty) return;

      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          SnackBar(
            content: Text(message),
            backgroundColor: Colors.red.shade800,
          ),
        );
    }

    return AppDialogShell(
      title: 'Cambiar contraseña',
      description:
          'Completa los campos para actualizar tu contraseña de forma segura.',
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          AppFormLayout(
            submitText: 'Guardar cambios',
            onSubmit: formState.isPosting ? null : onSubmit,
            fields: [
              CustomTextFormField(
                label: 'Contraseña actual',
                obscureText: true,
                onChanged: formNotifier.onCurrentPasswordChange,
                errorMessage: formState.currentPasswordError,
              ),
              CustomTextFormField(
                label: 'Nueva contraseña',
                obscureText: true,
                onChanged: formNotifier.onNewPasswordChange,
                errorMessage: formState.newPasswordError,
              ),
              CustomTextFormField(
                label: 'Confirmar nueva contraseña',
                obscureText: true,
                onChanged: formNotifier.onConfirmNewPasswordChange,
                errorMessage: formState.confirmPasswordError,
              ),
            ],
          ),
          const SizedBox(height: 10),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: formState.isPosting
                  ? null
                  : () => Navigator.of(context).pop(false),
              child: const Text('Cancelar'),
            ),
          ),
        ],
      ),
    );
  }
}
