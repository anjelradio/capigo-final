import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/shared/shared.dart';

class RequestServiceAudioControls extends StatelessWidget {
  const RequestServiceAudioControls({
    super.key,
    required this.hasAudio,
    required this.isRecordingAudio,
    required this.isPlayingAudio,
    required this.isPosting,
    required this.onStartRecordingTap,
    required this.onStopRecordingTap,
    required this.onPlayAudioTap,
    required this.onStopAudioTap,
    required this.onClearAudioTap,
  });

  final bool hasAudio;
  final bool isRecordingAudio;
  final bool isPlayingAudio;
  final bool isPosting;
  final VoidCallback onStartRecordingTap;
  final VoidCallback onStopRecordingTap;
  final VoidCallback onPlayAudioTap;
  final VoidCallback onStopAudioTap;
  final VoidCallback onClearAudioTap;

  @override
  Widget build(BuildContext context) {
    final statusText = isRecordingAudio
        ? 'Grabando audio... toca detener cuando termines.'
        : hasAudio
        ? 'Audio listo para enviar.'
        : 'Toca grabar para reportar el incidente por voz.';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: double.infinity,
          height: 46,
          child: CustomFilledButton(
            text: isRecordingAudio ? 'Detener grabacion' : 'Grabar audio',
            onPressed: isPosting
                ? null
                : (isRecordingAudio ? onStopRecordingTap : onStartRecordingTap),
            buttonColor: isRecordingAudio
                ? AppColors.toastError
                : AppColors.appAccent,
            textColor: isRecordingAudio
                ? AppColors.appTextOnDark
                : AppColors.appAccentText,
            borderRadius: 14,
          ),
        ),
        if (!isRecordingAudio && hasAudio) ...[
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: SizedBox(
                  height: 42,
                  child: OutlinedButton.icon(
                    onPressed: isPosting
                        ? null
                        : (isPlayingAudio ? onStopAudioTap : onPlayAudioTap),
                    icon: Icon(
                      isPlayingAudio
                          ? Icons.stop_rounded
                          : Icons.volume_up_rounded,
                      size: 18,
                      color: AppColors.appTextOnDark,
                    ),
                    label: Text(
                      isPlayingAudio ? 'Detener audio' : 'Escuchar',
                      style: const TextStyle(
                        color: AppColors.appTextOnDark,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: AppColors.appAccentDeep),
                      backgroundColor: AppColors.appBgDeep,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: SizedBox(
                  height: 42,
                  child: OutlinedButton.icon(
                    onPressed: isPosting ? null : onClearAudioTap,
                    icon: const Icon(
                      Icons.delete_outline_rounded,
                      size: 18,
                      color: AppColors.appTextOnDark,
                    ),
                    label: const Text(
                      'Limpiar',
                      style: TextStyle(
                        color: AppColors.appTextOnDark,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: AppColors.appAccentDeep),
                      backgroundColor: AppColors.appBgDeep,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
        const SizedBox(height: 8),
        Text(
          statusText,
          style: const TextStyle(
            color: AppColors.appTextOnDarkMuted,
            fontSize: 12,
          ),
        ),
      ],
    );
  }
}
