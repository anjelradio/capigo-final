import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';

class AppDialogShell extends StatelessWidget {
  final String title;
  final String description;
  final Widget child;
  final VoidCallback? onCancel;
  final String cancelText;

  const AppDialogShell({
    super.key,
    required this.title,
    required this.description,
    required this.child,
    this.onCancel,
    this.cancelText = 'Cancelar',
  });

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Dialog(
      backgroundColor: AppColors.appCardBg,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: textTheme.titleSmall?.copyWith(
                color: AppColors.appAccentDeep,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              description,
              style: textTheme.bodySmall?.copyWith(
                color: AppColors.appTextSecondary,
                height: 1.35,
              ),
            ),
            const SizedBox(height: 14),
            child,
            if (onCancel != null) ...[
              const SizedBox(height: 8),
              Align(
                alignment: Alignment.centerRight,
                child: TextButton(onPressed: onCancel, child: Text(cancelText)),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
