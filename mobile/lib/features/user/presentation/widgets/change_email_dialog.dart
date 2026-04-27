import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/features/shared/shared.dart';
import 'package:mobile/features/user/presentation/providers/providers.dart';

class ChangeEmailDialog extends ConsumerWidget {
  const ChangeEmailDialog({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final formState = ref.watch(emailChangeFormProvider);
    final formNotifier = ref.read(emailChangeFormProvider.notifier);

    Future<void> onVerifyOtp() async {
      final isSuccess = await formNotifier.verifyOtp();
      if (!context.mounted) return;

      if (isSuccess) {
        ScaffoldMessenger.of(context)
          ..hideCurrentSnackBar()
          ..showSnackBar(
            const SnackBar(
              content: Text('Codigo OTP verificado correctamente'),
              backgroundColor: Color(0xFF2E7D32),
            ),
          );
        return;
      }

      final message = ref.read(emailChangeFormProvider).errorMessage;
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

    Future<void> onSubmitNewEmail() async {
      final isSuccess = await formNotifier.submitNewEmail();
      if (!context.mounted) return;

      if (isSuccess) {
        Navigator.of(context).pop(true);
        return;
      }

      final message = ref.read(emailChangeFormProvider).errorMessage;
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

    final isOtpStep = formState.step == EmailChangeStep.otp;

    return AppDialogShell(
      title: isOtpStep ? 'Verificar codigo OTP' : 'Ingresa tu nuevo correo',
      description: isOtpStep
          ? 'Se te envio un codigo OTP a tu correo actual. Ingresalo para continuar.'
          : 'Introduce el nuevo correo para actualizar tu cuenta.',
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          AppFormLayout(
            submitText: isOtpStep ? 'Validar codigo OTP' : 'Guardar cambios',
            onSubmit: formState.isPosting
                ? null
                : isOtpStep
                ? onVerifyOtp
                : onSubmitNewEmail,
            fields: [
              if (isOtpStep)
                CustomTextFormField(
                  label: 'Codigo OTP',
                  hint: '000000',
                  keyboardType: TextInputType.number,
                  onChanged: formNotifier.onOtpChange,
                  errorMessage: formState.isOtpFormPosted
                      ? formState.otp.errorMessage
                      : null,
                )
              else
                CustomTextFormField(
                  label: 'Nuevo correo electronico',
                  keyboardType: TextInputType.emailAddress,
                  onChanged: formNotifier.onNewEmailChange,
                  errorMessage: formState.isNewEmailFormPosted
                      ? formState.newEmail.errorMessage
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
                  : () {
                      if (isOtpStep) {
                        Navigator.of(context).pop(false);
                        return;
                      }
                      formNotifier.goToOtpStep();
                    },
              child: Text(isOtpStep ? 'Cancelar' : 'Volver'),
            ),
          ),
        ],
      ),
    );
  }
}
