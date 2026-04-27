import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

const appFont = GoogleFonts.spaceGrotesk;

class AppColors {
  // Brand palette
  static const appBgBase = Color(0xFF1F242B);
  static const appBgMid = Color(0xFF24303E);
  static const appBgDeep = Color(0xFF161B21);

  static const appAccent = Color(0xFFF4BF14);
  static const appAccentHover = Color(0xFFDFAC0F);
  static const appAccentDeep = Color(0xFFB0892D);
  static const appAccentText = Color(0xFF1F1B12);

  static const appTextOnDark = Color(0xFFF2F4F7);
  static const appTextOnDarkMuted = Color(0xFFB6BEC8);

  // Nav/Header
  static const appNavBg = Color(0xE03A3F46);
  static const appNavBorder = Color(0x24FFFFFF);
  static const appNavText = Color(0xFFC5CCD5);

  // Surfaces
  static const appCardBg = Color(0xFFFFFFFF);
  static const appCardSoftBg = Color(0xFFECECEC);
  static const appCardSoftBorder = Color(0xFFD8D8D8);
  static const appCardBorder = Color(0x1A111827);
  static const appTextPrimary = Color(0xFF171A1F);
  static const appTextSecondary = Color(0xFF596272);

  // Auth
  static const authInputBg = Color(0xF0FFFFFF);
  static const authInputBorder = Color(0x52FFFFFF);
  static const authInputFocus = appAccent;
  static const authLabelText = Color(0xFFDCE2E9);
  static const authLink = Color(0xFF8A6D11);

  // Toasts
  static const toastSuccess = Color(0xFF1F7A59);
  static const toastError = Color(0xFFB93C4B);
  static const toastInfo = Color(0xFF3F7F9A);
  static const toastWarning = Color(0xFFB0892D);
}

class AppTheme {
  ThemeData getTheme() => ThemeData(
    ///* General
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: AppColors.appAccent,
      primary: AppColors.appAccent,
      onPrimary: AppColors.appAccentText,
      surface: AppColors.appBgBase,
      onSurface: AppColors.appTextOnDark,
    ),

    ///* Texts
    textTheme: TextTheme(
      titleLarge: appFont().copyWith(fontSize: 40, fontWeight: FontWeight.bold),
      titleMedium: appFont().copyWith(
        fontSize: 25,
        fontWeight: FontWeight.bold,
      ),
      titleSmall: appFont().copyWith(fontSize: 20),
      bodyMedium: appFont().copyWith(fontSize: 18),
      bodySmall: appFont().copyWith(fontSize: 15),
    ),

    ///* Scaffold Background Color
    scaffoldBackgroundColor: AppColors.appBgBase,

    ///* Buttons
    filledButtonTheme: FilledButtonThemeData(
      style: ButtonStyle(
        backgroundColor: const WidgetStatePropertyAll(AppColors.appAccent),
        foregroundColor: const WidgetStatePropertyAll(AppColors.appAccentText),
        shape: WidgetStatePropertyAll(
          RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        ),
        textStyle: WidgetStatePropertyAll(
          appFont().copyWith(fontWeight: FontWeight.w700),
        ),
      ),
    ),

    ///* AppBar
    appBarTheme: AppBarTheme(
      backgroundColor: AppColors.appBgBase,
      foregroundColor: AppColors.appTextOnDark,
      titleTextStyle: appFont().copyWith(
        fontSize: 25,
        fontWeight: FontWeight.bold,
        color: AppColors.appTextOnDark,
      ),
    ),
  );
}
