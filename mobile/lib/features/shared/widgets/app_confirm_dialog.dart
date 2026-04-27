import 'package:flutter/material.dart';

import 'app_dialog_shell.dart';
import 'custom_filled_button.dart';

class AppConfirmDialog extends StatelessWidget {
  final String title;
  final String description;
  final String confirmText;
  final String cancelText;

  const AppConfirmDialog({
    super.key,
    required this.title,
    required this.description,
    required this.confirmText,
    this.cancelText = 'Cancelar',
  });

  @override
  Widget build(BuildContext context) {
    return AppDialogShell(
      title: title,
      description: description,
      child: Row(
        children: [
          Expanded(
            child: OutlinedButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: Text(cancelText),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: CustomFilledButton(
              text: confirmText,
              onPressed: () => Navigator.of(context).pop(true),
            ),
          ),
        ],
      ),
    );
  }
}
