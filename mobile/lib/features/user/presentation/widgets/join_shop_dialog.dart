import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/features/shared/shared.dart';
import 'package:mobile/features/user/presentation/providers/providers.dart';

class JoinShopDialog extends ConsumerWidget {
  const JoinShopDialog({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final formState = ref.watch(joinShopFormProvider);
    final formNotifier = ref.read(joinShopFormProvider.notifier);

    Future<void> onSubmit() async {
      final isSuccess = await formNotifier.submit();
      if (!context.mounted) return;

      if (isSuccess) {
        Navigator.of(context).pop(true);
        return;
      }

      final message = ref.read(joinShopFormProvider).errorMessage;
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
      title: 'Unirse a un taller',
      description: 'Ingresa el codigo de invitacion de 6 caracteres.',
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          AppFormLayout(
            submitText: formState.isPosting ? 'Uniendo...' : 'Unirme al taller',
            onSubmit: formState.isPosting ? null : onSubmit,
            fields: [
              CustomTextFormField(
                label: 'Codigo de invitacion',
                initialValue: formState.code.value,
                onChanged: formNotifier.onCodeChanged,
                errorMessage: formState.isFormPosted
                    ? formState.code.errorMessage
                    : null,
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
