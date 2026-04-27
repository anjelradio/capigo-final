import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/incidents/presentation/providers/providers.dart';
import 'package:mobile/features/incidents/presentation/widgets/client/request_service/request_service_audio_controls.dart';

class RequestServiceDescriptionSection extends StatelessWidget {
  const RequestServiceDescriptionSection({
    super.key,
    required this.controller,
    required this.inputMode,
    required this.hasAudio,
    required this.isRecordingAudio,
    required this.isPlayingAudio,
    required this.isPosting,
    required this.onInputModeChanged,
    required this.onStartRecordingTap,
    required this.onStopRecordingTap,
    required this.onPlayAudioTap,
    required this.onStopAudioTap,
    required this.onClearAudioTap,
  });

  final TextEditingController controller;
  final IncidentInputMode inputMode;
  final bool hasAudio;
  final bool isRecordingAudio;
  final bool isPlayingAudio;
  final bool isPosting;
  final ValueChanged<IncidentInputMode> onInputModeChanged;
  final VoidCallback onStartRecordingTap;
  final VoidCallback onStopRecordingTap;
  final VoidCallback onPlayAudioTap;
  final VoidCallback onStopAudioTap;
  final VoidCallback onClearAudioTap;

  @override
  Widget build(BuildContext context) {
    final isTextMode = inputMode == IncidentInputMode.text;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.appBgMid,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Incidente',
            style: TextStyle(
              color: AppColors.appAccent,
              fontWeight: FontWeight.w800,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 10),
          _InputModeSelector(
            inputMode: inputMode,
            isPosting: isPosting,
            onInputModeChanged: onInputModeChanged,
          ),
          const SizedBox(height: 12),
          if (isTextMode)
            _TextDescriptionField(controller: controller, isPosting: isPosting)
          else
            RequestServiceAudioControls(
              hasAudio: hasAudio,
              isRecordingAudio: isRecordingAudio,
              isPlayingAudio: isPlayingAudio,
              isPosting: isPosting,
              onStartRecordingTap: onStartRecordingTap,
              onStopRecordingTap: onStopRecordingTap,
              onPlayAudioTap: onPlayAudioTap,
              onStopAudioTap: onStopAudioTap,
              onClearAudioTap: onClearAudioTap,
            ),
        ],
      ),
    );
  }
}

class _InputModeSelector extends StatelessWidget {
  const _InputModeSelector({
    required this.inputMode,
    required this.isPosting,
    required this.onInputModeChanged,
  });

  final IncidentInputMode inputMode;
  final bool isPosting;
  final ValueChanged<IncidentInputMode> onInputModeChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 56,
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: AppColors.appBgDeep,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppColors.appAccentDeep),
      ),
      child: Row(
        children: [
          Expanded(
            child: _ModeSegment(
              label: 'Texto',
              icon: Icons.short_text_rounded,
              isSelected: inputMode == IncidentInputMode.text,
              onTap: isPosting
                  ? null
                  : () => onInputModeChanged(IncidentInputMode.text),
            ),
          ),
          const SizedBox(width: 6),
          Expanded(
            child: _ModeSegment(
              label: 'Audio',
              icon: Icons.graphic_eq_rounded,
              isSelected: inputMode == IncidentInputMode.audio,
              onTap: isPosting
                  ? null
                  : () => onInputModeChanged(IncidentInputMode.audio),
            ),
          ),
        ],
      ),
    );
  }
}

class _ModeSegment extends StatelessWidget {
  const _ModeSegment({
    required this.label,
    required this.icon,
    required this.isSelected,
    required this.onTap,
  });

  final String label;
  final IconData icon;
  final bool isSelected;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: isSelected ? AppColors.appAccent : Colors.transparent,
      borderRadius: BorderRadius.circular(10),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(10),
        child: Center(
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                icon,
                size: 18,
                color: isSelected
                    ? AppColors.appAccentText
                    : AppColors.appTextOnDark,
              ),
              const SizedBox(width: 7),
              Text(
                label,
                style: TextStyle(
                  color: isSelected
                      ? AppColors.appAccentText
                      : AppColors.appTextOnDark,
                  fontWeight: FontWeight.w700,
                  fontSize: 14,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _TextDescriptionField extends StatelessWidget {
  const _TextDescriptionField({
    required this.controller,
    required this.isPosting,
  });

  final TextEditingController controller;
  final bool isPosting;

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      maxLines: 5,
      enabled: !isPosting,
      style: const TextStyle(color: AppColors.appTextOnDark),
      cursorColor: AppColors.appAccent,
      decoration: InputDecoration(
        hintText:
            'Ejemplo: Se apago el auto en carretera y no vuelve a encender.',
        hintStyle: const TextStyle(color: AppColors.appTextOnDarkMuted),
        filled: true,
        fillColor: AppColors.appBgDeep,
        contentPadding: const EdgeInsets.all(14),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: AppColors.appAccentDeep),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: AppColors.appAccent, width: 1.4),
        ),
      ),
    );
  }
}
