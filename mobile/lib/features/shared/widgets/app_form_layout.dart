import 'package:flutter/material.dart';

import 'custom_filled_button.dart';

class AppFormLayout extends StatelessWidget {
  const AppFormLayout({
    super.key,
    required this.fields,
    required this.submitText,
    required this.onSubmit,
    this.fieldSpacing = 20,
    this.submitButtonColor,
    this.submitButtonHeight = 48,
  });

  final List<Widget> fields;
  final String submitText;
  final VoidCallback? onSubmit;
  final double fieldSpacing;
  final Color? submitButtonColor;
  final double submitButtonHeight;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ..._withSpacing(fields, fieldSpacing),
        const SizedBox(height: 24),
        SizedBox(
          width: double.infinity,
          height: submitButtonHeight,
          child: CustomFilledButton(
            text: submitText,
            buttonColor: submitButtonColor,
            onPressed: onSubmit == null
                ? null
                : () {
                    FocusManager.instance.primaryFocus?.unfocus();
                    onSubmit!.call();
                  },
          ),
        ),
      ],
    );
  }

  List<Widget> _withSpacing(List<Widget> widgets, double spacing) {
    if (widgets.isEmpty) return const [];

    final result = <Widget>[];
    for (var index = 0; index < widgets.length; index++) {
      result.add(widgets[index]);
      if (index < widgets.length - 1) {
        result.add(SizedBox(height: spacing));
      }
    }
    return result;
  }
}
