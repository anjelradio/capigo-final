import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/incidents/presentation/providers/providers.dart';
import 'package:mobile/features/incidents/presentation/widgets/widgets.dart';
import 'package:mobile/features/user/presentation/providers/providers.dart';

class RequestServiceScreen extends ConsumerStatefulWidget {
  const RequestServiceScreen({super.key});

  @override
  ConsumerState<RequestServiceScreen> createState() =>
      _RequestServiceScreenState();
}

class _RequestServiceScreenState extends ConsumerState<RequestServiceScreen> {
  final _descriptionController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _descriptionController.addListener(_onDescriptionChanged);
    Future.microtask(() {
      final vehiclesState = ref.read(vehiclesProvider);
      if (!vehiclesState.hasLoaded && !vehiclesState.isLoading) {
        ref.read(vehiclesProvider.notifier).loadVehicles();
      }

      final locationState = ref.read(deviceLocationProvider);
      if (!locationState.hasLoaded && !locationState.isLoading) {
        ref.read(deviceLocationProvider.notifier).loadCurrentLocation();
      }
    });
  }

  @override
  void dispose() {
    _descriptionController.removeListener(_onDescriptionChanged);
    _descriptionController.dispose();
    super.dispose();
  }

  void _onDescriptionChanged() {
    ref
        .read(requestServiceFormProvider.notifier)
        .onDescriptionChanged(_descriptionController.text);
  }

  @override
  Widget build(BuildContext context) {
    final vehiclesState = ref.watch(vehiclesProvider);
    final locationState = ref.watch(deviceLocationProvider);
    final formState = ref.watch(requestServiceFormProvider);
    final formNotifier = ref.read(requestServiceFormProvider.notifier);

    return Scaffold(
      backgroundColor: AppColors.appBgBase,
      appBar: AppBar(
        title: const Text('Solicitar ayuda'),
        foregroundColor: AppColors.appAccent,
        iconTheme: const IconThemeData(color: AppColors.appAccent),
        titleTextStyle: Theme.of(context).textTheme.titleSmall?.copyWith(
          color: AppColors.appAccent,
          fontWeight: FontWeight.w800,
        ),
        actions: [
          IconButton(
            tooltip: 'Tomar foto',
            onPressed: formState.isPosting
                ? null
                : formNotifier.addPhotoFromCamera,
            icon: const Icon(Icons.photo_camera_outlined),
          ),
          IconButton(
            tooltip: 'Abrir galeria',
            onPressed: formState.isPosting
                ? null
                : formNotifier.addPhotosFromGallery,
            icon: const Icon(Icons.photo_library_outlined),
          ),
        ],
        centerTitle: true,
      ),
      bottomNavigationBar: RequestServiceSubmitBar(
        isPosting: formState.isPosting,
        onSubmit: formState.isPosting
            ? null
            : formState.canSubmit
            ? () async {
                final messenger = ScaffoldMessenger.of(context);

                if (!locationState.hasLocation) {
                  await ref
                      .read(deviceLocationProvider.notifier)
                      .refreshLocation();
                }

                final resolvedLocation = ref.read(deviceLocationProvider);
                if (!resolvedLocation.hasLocation) {
                  messenger
                    ..hideCurrentSnackBar()
                    ..showSnackBar(
                      const SnackBar(
                        content: Text(
                          'No fue posible obtener tu ubicacion actual para enviar el incidente.',
                        ),
                        backgroundColor: AppColors.toastWarning,
                      ),
                    );
                  return;
                }

                final submissionOutcome = await formNotifier.submitIncident(
                  latitude: resolvedLocation.latitude!,
                  longitude: resolvedLocation.longitude!,
                );
                if (!context.mounted) return;

                if (submissionOutcome == RequestServiceSubmissionOutcome.sent) {
                  _descriptionController.clear();
                  messenger
                    ..hideCurrentSnackBar()
                    ..showSnackBar(
                      const SnackBar(
                        content: Text('Solicitud enviada correctamente.'),
                        backgroundColor: AppColors.toastInfo,
                      ),
                    );
                  context.go('/incidents/active-service');
                } else if (submissionOutcome == RequestServiceSubmissionOutcome.queued) {
                  _descriptionController.clear();
                  messenger
                    ..hideCurrentSnackBar()
                    ..showSnackBar(
                      const SnackBar(
                        content: Text(
                          'Sin conexion. La solicitud quedo pendiente y se enviara automaticamente.',
                        ),
                        backgroundColor: AppColors.toastWarning,
                      ),
                    );
                } else {
                  final latestFormState = ref.read(requestServiceFormProvider);
                  final fallbackError = latestFormState.errorMessage.isNotEmpty
                      ? latestFormState.errorMessage
                      : 'No fue posible enviar la solicitud de ayuda.';
                  messenger
                    ..hideCurrentSnackBar()
                    ..showSnackBar(
                      SnackBar(
                        content: Text(fallbackError),
                        backgroundColor: AppColors.toastWarning,
                      ),
                    );
                }
              }
            : () {
                ScaffoldMessenger.of(context)
                  ..hideCurrentSnackBar()
                  ..showSnackBar(
                    const SnackBar(
                      content: Text(
                        'Selecciona vehiculo, agrega foto y completa el incidente en texto o audio.',
                      ),
                      backgroundColor: AppColors.toastWarning,
                    ),
                  );
              },
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            RequestServiceVehicleSelector(
              vehicles: vehiclesState.vehicles,
              isLoading: vehiclesState.isLoading,
              selectedVehicleId: formState.selectedVehicleId,
              onChanged: formNotifier.onVehicleChanged,
            ),
            const SizedBox(height: 14),
            RequestServiceDescriptionSection(
              controller: _descriptionController,
              inputMode: formState.inputMode,
              hasAudio: formState.hasAudioIncident,
              isRecordingAudio: formState.isRecordingAudio,
              isPlayingAudio: formState.isPlayingAudio,
              isPosting: formState.isPosting,
              onInputModeChanged: formNotifier.onInputModeChanged,
              onStartRecordingTap: formNotifier.startAudioRecording,
              onStopRecordingTap: formNotifier.stopAudioRecording,
              onPlayAudioTap: formNotifier.playRecordedAudio,
              onStopAudioTap: formNotifier.stopAudioPlayback,
              onClearAudioTap: formNotifier.clearAudio,
            ),
            const SizedBox(height: 14),
            RequestServiceAttachmentsSection(
              imagePaths: formState.imagePaths,
              onRemoveImageTap: formNotifier.removeImageAt,
            ),
            const SizedBox(height: 10),
            Text(
              formState.isPosting
                  ? 'Enviando solicitud de ayuda...'
                  : formState.canSubmit
                  ? 'Formulario listo para enviar.'
                  : 'Completa todos los campos requeridos para habilitar el envio.',
              style: const TextStyle(
                color: AppColors.appTextOnDarkMuted,
                fontSize: 12,
              ),
            ),
            if (formState.errorMessage.isNotEmpty) ...[
              const SizedBox(height: 6),
              Text(
                formState.errorMessage,
                style: const TextStyle(
                  color: AppColors.toastWarning,
                  fontSize: 12,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
