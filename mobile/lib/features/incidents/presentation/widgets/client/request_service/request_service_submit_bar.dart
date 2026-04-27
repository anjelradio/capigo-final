import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/shared/shared.dart';

class RequestServiceSubmitBar extends StatelessWidget {
  const RequestServiceSubmitBar({
    super.key,
    this.onSubmit,
    this.isPosting = false,
  });

  final VoidCallback? onSubmit;
  final bool isPosting;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      minimum: const EdgeInsets.fromLTRB(16, 10, 16, 14),
      child: SizedBox(
        height: 54,
        child: CustomFilledButton(
          text: isPosting ? 'Solicitando...' : 'Enviar solicitud',
          onPressed: onSubmit,
          buttonColor: AppColors.appAccent,
          textColor: AppColors.appAccentText,
          borderRadius: 22,
        ),
      ),
    );
  }
}
