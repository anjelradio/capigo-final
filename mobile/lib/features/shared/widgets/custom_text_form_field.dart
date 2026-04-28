import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';

class CustomTextFormField extends StatelessWidget {
  final String? label;
  final String? hint;
  final String? initialValue;
  final String? errorMessage;
  final bool obscureText;
  final bool readOnly;
  final TextInputType? keyboardType;
  final TextEditingController? controller;
  final Function(String)? onChanged;
  final Function(String)? onFieldSubmitted;
  final String? Function(String?)? validator;
  final Widget? suffixIcon;
  final Widget? prefixIcon;
  final Color? borderColor;
  final Color? focusColor;
  final Color? labelColor;
  final Color? fillColor;
  final Color? textColor;
  final Color? hintColor;
  final Color? errorColor;
  final double borderRadius;
  final int maxLines;
  final int? minLines;

  const CustomTextFormField({
    super.key,
    this.label,
    this.hint,
    this.initialValue,
    this.errorMessage,
    this.obscureText = false,
    this.readOnly = false,
    this.keyboardType = TextInputType.text,
    this.controller,
    this.onChanged,
    this.onFieldSubmitted,
    this.validator,
    this.suffixIcon,
    this.prefixIcon,
    this.borderColor,
    this.focusColor,
    this.labelColor,
    this.fillColor,
    this.textColor,
    this.hintColor,
    this.errorColor,
    this.borderRadius = 25,
    this.maxLines = 1,
    this.minLines,
  });

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final accentColor = focusColor ?? AppColors.appAccentDeep;
    final inputBorderColor = borderColor ?? AppColors.appAccentDeep;
    final inputLabelColor = labelColor ?? AppColors.appAccentDeep;
    final inputFillColor = fillColor ?? AppColors.authInputBg;
    final inputTextColor = textColor ?? AppColors.appTextPrimary;
    final inputHintColor = hintColor ?? AppColors.appTextSecondary;
    final inputErrorColor = errorColor ?? AppColors.toastError;

    final border = OutlineInputBorder(
      borderRadius: BorderRadius.circular(borderRadius),
      borderSide: BorderSide(color: inputBorderColor, width: 1.2),
    );

    final focusedBorder = OutlineInputBorder(
      borderRadius: BorderRadius.circular(borderRadius),
      borderSide: BorderSide(color: accentColor, width: 1.6),
    );

    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(borderRadius),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.07),
            blurRadius: 16,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: TextFormField(
        controller: controller,
        initialValue: controller == null ? initialValue : null,
        onChanged: onChanged,
        validator: validator,
        onFieldSubmitted: onFieldSubmitted,
        obscureText: obscureText,
        readOnly: readOnly,
        keyboardType: keyboardType,
        maxLines: obscureText ? 1 : maxLines,
        minLines: obscureText ? null : minLines,
        style: textTheme.bodyMedium?.copyWith(
          color: inputTextColor,
          fontSize: 15,
          fontWeight: FontWeight.w500,
        ),
        cursorColor: accentColor,
        decoration: InputDecoration(
          labelText: label,
          hintText: hint,
          errorText: errorMessage,
          prefixIcon: prefixIcon,
          suffixIcon: suffixIcon,

          filled: true,
          fillColor: inputFillColor,

          contentPadding: const EdgeInsets.symmetric(
            horizontal: 18,
            vertical: 18,
          ),

          labelStyle: textTheme.bodyMedium?.copyWith(
            color: inputLabelColor,
            fontWeight: FontWeight.w500,
          ),

          floatingLabelStyle: textTheme.bodyMedium?.copyWith(
            color: accentColor,
            fontWeight: FontWeight.w700,
          ),

          hintStyle: textTheme.bodyMedium?.copyWith(
            color: inputHintColor,
            fontWeight: FontWeight.w400,
          ),

          enabledBorder: border,
          focusedBorder: focusedBorder,

          errorBorder: border.copyWith(
            borderSide: BorderSide(color: inputErrorColor, width: 1.2),
          ),

          focusedErrorBorder: focusedBorder.copyWith(
            borderSide: BorderSide(color: inputErrorColor, width: 1.6),
          ),
        ),
      ),
    );
  }
}
