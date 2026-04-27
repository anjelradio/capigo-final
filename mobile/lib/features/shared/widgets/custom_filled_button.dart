import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';

class CustomFilledButton extends StatelessWidget {
  static const Color defaultButtonColor = AppColors.appAccent;

  final void Function()? onPressed;
  final String text;
  final Color? buttonColor;
  final Color? textColor;
  final double borderRadius;
  final EdgeInsetsGeometry? padding;
  final TextStyle? textStyle;

  const CustomFilledButton({
    super.key,
    this.onPressed,
    required this.text,
    this.buttonColor,
    this.textColor,
    this.borderRadius = 25,
    this.padding,
    this.textStyle,
  });

  @override
  Widget build(BuildContext context) {
    final radius = BorderRadius.circular(borderRadius);

    return FilledButton(
      style: FilledButton.styleFrom(
        backgroundColor: buttonColor ?? defaultButtonColor,
        foregroundColor: textColor ?? AppColors.appAccentText,
        elevation: 0,
        padding:
            padding ?? const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: radius),
        shadowColor: Colors.transparent,
        textStyle: textStyle,
      ),

      onPressed: onPressed,
      child: Text(text),
    );
  }
}
