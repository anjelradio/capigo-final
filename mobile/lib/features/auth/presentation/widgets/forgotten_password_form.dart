import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/auth/auth.dart';
import 'package:mobile/features/shared/shared.dart';

class ForgottenPasswordForm extends ConsumerWidget {
  const ForgottenPasswordForm({super.key, this.textStyle});

  final TextStyle? textStyle;

  void _showSnackbar(
    BuildContext context,
    String message, {
    bool isError = true,
  }) {
    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError
            ? AppColors.toastError
            : AppColors.toastSuccess,
      ),
    );
  }

  Future<void> _onForgotPasswordPressed(
    BuildContext context,
    WidgetRef ref,
  ) async {
    ref.read(forgottenPasswordFormProvider.notifier).reset();
    await _openRequestOtpDialog(context, ref);
  }

  Future<void> _openRequestOtpDialog(
    BuildContext context,
    WidgetRef ref,
  ) async {
    await showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) {
        return Consumer(
          builder: (context, ref, _) {
            final formState = ref.watch(forgottenPasswordFormProvider);
            final notifier = ref.read(forgottenPasswordFormProvider.notifier);

            return AppDialogShell(
              title: 'Recuperar contrasena',
              description:
                  'Ingresa el correo de tu cuenta para enviarte un codigo OTP de recuperacion.',
              child: AppFormLayout(
                fields: [
                  CustomTextFormField(
                    label: 'Correo de la cuenta',
                    keyboardType: TextInputType.emailAddress,
                    onChanged: notifier.onEmailChange,
                    errorMessage: formState.isEmailFormPosted
                        ? formState.email.errorMessage
                        : null,
                  ),
                ],
                submitText: 'Enviar codigo',
                onSubmit: formState.canRequestOtp
                    ? () async {
                        final wasSent = await notifier.requestOtp();
                        if (!context.mounted) return;

                        if (!wasSent) {
                          final message = ref
                              .read(forgottenPasswordFormProvider)
                              .errorMessage;
                          if (message.isNotEmpty) {
                            _showSnackbar(context, message);
                          }
                          return;
                        }

                        Navigator.of(dialogContext).pop();
                        _showSnackbar(
                          context,
                          'Se ha enviado un codigo OTP a tu correo.',
                          isError: false,
                        );

                        await _openVerifyOtpDialog(context, ref);
                      }
                    : null,
                fieldSpacing: 14,
                submitButtonHeight: 46,
              ),
              onCancel: () {
                notifier.reset();
                Navigator.of(dialogContext).pop();
              },
            );
          },
        );
      },
    );
  }

  Future<void> _openVerifyOtpDialog(BuildContext context, WidgetRef ref) async {
    await showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) {
        return Consumer(
          builder: (context, ref, _) {
            final formState = ref.watch(forgottenPasswordFormProvider);
            final notifier = ref.read(forgottenPasswordFormProvider.notifier);

            return AppDialogShell(
              title: 'Verificar codigo OTP',
              description:
                  'Ingresa el codigo OTP. Si es valido, te enviaremos una nueva contrasena a tu correo.',
              child: AppFormLayout(
                fields: [
                  CustomTextFormField(
                    label: 'Codigo OTP',
                    hint: 'Ingresa el codigo de 6 digitos',
                    keyboardType: TextInputType.number,
                    onChanged: notifier.onOtpChange,
                    errorMessage: formState.isOtpFormPosted
                        ? formState.otp.errorMessage
                        : null,
                  ),
                ],
                submitText: 'Verificar codigo',
                onSubmit: formState.canVerifyOtp
                    ? () async {
                        final isValidOtp = await notifier.verifyOtp();
                        if (!context.mounted) return;

                        if (!isValidOtp) {
                          final message = ref
                              .read(forgottenPasswordFormProvider)
                              .errorMessage;
                          if (message.isNotEmpty) {
                            _showSnackbar(context, message);
                          }
                          return;
                        }

                        notifier.reset();
                        Navigator.of(dialogContext).pop();
                        _showSnackbar(
                          context,
                          'Contrasena restaurada, revisa tu correo.',
                          isError: false,
                        );
                      }
                    : null,
                fieldSpacing: 14,
                submitButtonHeight: 46,
              ),
              onCancel: () {
                notifier.reset();
                Navigator.of(dialogContext).pop();
              },
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final baseTextStyle = Theme.of(context).textTheme.bodyMedium;

    return TextButton(
      onPressed: () => _onForgotPasswordPressed(context, ref),
      child: Text(
        'Olvidaste tu contrasena?',
        style:
            textStyle ??
            baseTextStyle?.copyWith(color: AppColors.authLink, fontSize: 14),
      ),
    );
  }
}
