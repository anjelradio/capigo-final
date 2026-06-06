import 'dart:async';
import 'dart:io';
import 'dart:math';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_riverpod/legacy.dart';
import 'package:just_audio/just_audio.dart';
import 'package:mobile/features/auth/data/errors/auth_errors.dart';
import 'package:mobile/features/incidents/data/offline/offline.dart';
import 'package:mobile/features/incidents/presentation/providers/request_service/incident_offline_queue_provider.dart';
import 'package:mobile/features/incidents/presentation/providers/request_service/request_service_repository_provider.dart';
import 'package:mobile/features/shared/shared.dart';
import 'package:record/record.dart';

enum IncidentInputMode { text, audio }

enum RequestServiceSubmissionOutcome { sent, queued, failed }

final requestServiceFormProvider =
    StateNotifierProvider.autoDispose<
      RequestServiceFormNotifier,
      RequestServiceFormState
    >((ref) {
      final incidentRepository = ref.watch(incidentRepositoryProvider);
      final offlineQueueService = ref.watch(incidentOfflineQueueServiceProvider);

      Future<void> submitIncident({
        required String vehicleId,
        String? description,
        String? audioPath,
        required double latitude,
        required double longitude,
        required List<String> imagePaths,
        required String clientRequestId,
      }) {
        return incidentRepository.createIncident(
          vehicleId: vehicleId,
          description: description,
          audioPath: audioPath,
          latitude: latitude,
          longitude: longitude,
          imagePaths: imagePaths,
          clientRequestId: clientRequestId,
        );
      }

      return RequestServiceFormNotifier(
        cameraGalleryService: CameraGalleryServiceImpl(),
        audioRecorder: AudioRecorder(),
        audioPlayer: AudioPlayer(),
        offlineQueueService: offlineQueueService,
        submitIncidentCallback: submitIncident,
      );
    });

class RequestServiceFormNotifier
    extends StateNotifier<RequestServiceFormState> {
  RequestServiceFormNotifier({
    required CameraGalleryService cameraGalleryService,
    required AudioRecorder audioRecorder,
    required AudioPlayer audioPlayer,
    required IncidentOfflineQueueService offlineQueueService,
    required this.submitIncidentCallback,
  }) : _cameraGalleryService = cameraGalleryService,
        _audioRecorder = audioRecorder,
        _audioPlayer = audioPlayer,
        _offlineQueueService = offlineQueueService,
        super(RequestServiceFormState()) {
    _playerStateSubscription = _audioPlayer.playerStateStream.listen((event) {
      final isPlaying = event.playing;
      if (state.isPlayingAudio != isPlaying) {
        state = state.copyWith(isPlayingAudio: isPlaying);
      }
    });
  }

  final CameraGalleryService _cameraGalleryService;
  final AudioRecorder _audioRecorder;
  final AudioPlayer _audioPlayer;
  final IncidentOfflineQueueService _offlineQueueService;
  StreamSubscription<PlayerState>? _playerStateSubscription;
  final Future<void> Function({
    required String vehicleId,
    String? description,
    String? audioPath,
    required double latitude,
    required double longitude,
    required List<String> imagePaths,
    required String clientRequestId,
  })
  submitIncidentCallback;

  void onVehicleChanged(String? vehicleId) {
    state = state.copyWith(
      selectedVehicleId: vehicleId,
      errorMessages: const [],
    );
  }

  void onInputModeChanged(IncidentInputMode mode) {
    state = state.copyWith(inputMode: mode, errorMessages: const []);
  }

  void onDescriptionChanged(String value) {
    state = state.copyWith(description: value, errorMessages: const []);
  }

  Future<void> addPhotoFromCamera() async {
    final path = await _cameraGalleryService.takePhoto();
    if (path == null) return;

    _addImagePaths([path]);
  }

  Future<void> addPhotosFromGallery() async {
    final paths = await _cameraGalleryService.selectPhotos();
    if (paths.isEmpty) return;

    _addImagePaths(paths);
  }

  void removeImageAt(int index) {
    if (index < 0 || index >= state.imagePaths.length) return;

    final nextPaths = [...state.imagePaths]..removeAt(index);
    state = state.copyWith(imagePaths: nextPaths, errorMessages: const []);
  }

  Future<void> startAudioRecording() async {
    if (state.isRecordingAudio || state.isPosting) return;

    final hasPermission = await _audioRecorder.hasPermission();
    if (!hasPermission) {
      state = state.copyWith(
        errorMessages: const ['Debes permitir el acceso al microfono.'],
      );
      return;
    }

    try {
      await _audioPlayer.stop();
      await _audioRecorder.start(
        const RecordConfig(
          encoder: AudioEncoder.aacLc,
          bitRate: 128000,
          sampleRate: 44100,
        ),
        path: _buildRecordingPath(),
      );

      state = state.copyWith(
        isRecordingAudio: true,
        isAudioPaused: false,
        isPlayingAudio: false,
        audioPath: null,
        errorMessages: const [],
      );
    } catch (_) {
      state = state.copyWith(
        isRecordingAudio: false,
        isAudioPaused: false,
        errorMessages: const ['No fue posible iniciar la grabacion.'],
      );
    }
  }

  Future<void> pauseAudioRecording() async {
    if (!state.isRecordingAudio || state.isAudioPaused || state.isPosting) {
      return;
    }

    try {
      await _audioRecorder.pause();
      state = state.copyWith(isAudioPaused: true, errorMessages: const []);
    } catch (_) {
      state = state.copyWith(
        errorMessages: const ['No fue posible pausar la grabacion.'],
      );
    }
  }

  Future<void> resumeAudioRecording() async {
    if (!state.isRecordingAudio || !state.isAudioPaused || state.isPosting) {
      return;
    }

    try {
      await _audioRecorder.resume();
      state = state.copyWith(isAudioPaused: false, errorMessages: const []);
    } catch (_) {
      state = state.copyWith(
        errorMessages: const ['No fue posible reanudar la grabacion.'],
      );
    }
  }

  Future<void> stopAudioRecording() async {
    if (!state.isRecordingAudio || state.isPosting) return;

    try {
      final audioPath = await _audioRecorder.stop();
      state = state.copyWith(
        isRecordingAudio: false,
        isAudioPaused: false,
        audioPath: audioPath,
        errorMessages: const [],
      );
    } catch (_) {
      state = state.copyWith(
        isRecordingAudio: false,
        isAudioPaused: false,
        errorMessages: const ['No fue posible guardar el audio.'],
      );
    }
  }

  Future<void> playRecordedAudio() async {
    final audioPath = state.audioPath;
    if (audioPath == null || audioPath.isEmpty || state.isPosting) return;

    try {
      await _audioPlayer.stop();
      await _audioPlayer.setFilePath(audioPath);
      await _audioPlayer.play();
      state = state.copyWith(isPlayingAudio: true, errorMessages: const []);
    } catch (_) {
      state = state.copyWith(
        isPlayingAudio: false,
        errorMessages: const ['No fue posible reproducir el audio.'],
      );
    }
  }

  Future<void> stopAudioPlayback() async {
    if (!state.isPlayingAudio) return;
    await _audioPlayer.stop();
    state = state.copyWith(isPlayingAudio: false);
  }

  Future<void> clearAudio() async {
    await _audioPlayer.stop();

    if (state.isRecordingAudio) {
      await _audioRecorder.stop();
    }

    state = state.copyWith(
      isRecordingAudio: false,
      isAudioPaused: false,
      isPlayingAudio: false,
      audioPath: null,
      errorMessages: const [],
    );
  }

  Future<RequestServiceSubmissionOutcome> submitIncident({
    required double latitude,
    required double longitude,
  }) async {
    final vehicleId = state.selectedVehicleId;
    final textDescription = state.description.trim();
    final audioPath = (state.audioPath ?? '').trim();

    if (!state.canSubmit || vehicleId == null) {
      state = state.copyWith(
        errorMessages: const [
          'Selecciona vehiculo, agrega foto y completa el incidente en texto o audio.',
        ],
      );
      return RequestServiceSubmissionOutcome.failed;
    }

    final descriptionToSend = state.inputMode == IncidentInputMode.text
        ? textDescription
        : null;
    final audioToSend = state.inputMode == IncidentInputMode.audio
        ? audioPath
        : null;
    final clientRequestId = _generateClientRequestId();

    state = state.copyWith(isPosting: true, errorMessages: const []);

    final connectivity = await Connectivity().checkConnectivity();
    if (_isOffline(connectivity)) {
      try {
        await _offlineQueueService.enqueueIncident(
          vehicleId: vehicleId,
          description: descriptionToSend,
          audioPath: audioToSend,
          latitude: latitude,
          longitude: longitude,
          imagePaths: state.imagePaths,
          clientRequestId: clientRequestId,
        );

        if (!mounted) return RequestServiceSubmissionOutcome.queued;
        await _audioPlayer.stop();
        state = RequestServiceFormState();
        return RequestServiceSubmissionOutcome.queued;
      } catch (error) {
        if (!mounted) return RequestServiceSubmissionOutcome.failed;
        final message = error is CustomError
            ? error.messages
            : const ['No fue posible guardar la solicitud sin conexion.'];
        state = state.copyWith(isPosting: false, errorMessages: message);
        return RequestServiceSubmissionOutcome.failed;
      }
    }

    try {
      await submitIncidentCallback(
        vehicleId: vehicleId,
        description: descriptionToSend,
        audioPath: audioToSend,
        latitude: latitude,
        longitude: longitude,
        imagePaths: state.imagePaths,
        clientRequestId: clientRequestId,
      );

      if (!mounted) return RequestServiceSubmissionOutcome.sent;
      await _audioPlayer.stop();
      state = RequestServiceFormState();
      return RequestServiceSubmissionOutcome.sent;
    } on CustomError catch (error) {
      final isConnectionIssue = error.messages.any(
        (message) => message.toLowerCase().contains('conexion'),
      );
      if (isConnectionIssue) {
        try {
          await _offlineQueueService.enqueueIncident(
            vehicleId: vehicleId,
            description: descriptionToSend,
            audioPath: audioToSend,
            latitude: latitude,
            longitude: longitude,
            imagePaths: state.imagePaths,
            clientRequestId: clientRequestId,
          );

          if (!mounted) return RequestServiceSubmissionOutcome.queued;
          await _audioPlayer.stop();
          state = RequestServiceFormState();
          return RequestServiceSubmissionOutcome.queued;
        } catch (queueError) {
          if (!mounted) return RequestServiceSubmissionOutcome.failed;
          final message = queueError is CustomError
              ? queueError.messages
              : const ['No fue posible guardar la solicitud sin conexion.'];
          state = state.copyWith(isPosting: false, errorMessages: message);
          return RequestServiceSubmissionOutcome.failed;
        }
      }

      if (!mounted) return RequestServiceSubmissionOutcome.failed;
      state = state.copyWith(isPosting: false, errorMessages: error.messages);
      return RequestServiceSubmissionOutcome.failed;
    } catch (_) {
      if (!mounted) return RequestServiceSubmissionOutcome.failed;
      state = state.copyWith(
        isPosting: false,
        errorMessages: const ['No fue posible enviar la solicitud de ayuda.'],
      );
      return RequestServiceSubmissionOutcome.failed;
    }
  }

  void _addImagePaths(List<String> paths) {
    final uniquePaths = [...state.imagePaths];
    for (final path in paths) {
      if (!uniquePaths.contains(path)) {
        uniquePaths.add(path);
      }
    }

    state = state.copyWith(imagePaths: uniquePaths, errorMessages: const []);
  }

  String _buildRecordingPath() {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    return '${Directory.systemTemp.path}/incident_audio_$timestamp.m4a';
  }

  String _generateClientRequestId() {
    final timestamp = DateTime.now().toUtc().microsecondsSinceEpoch.toRadixString(36);
    final randomPart = Random().nextInt(1 << 32).toRadixString(36);
    return 'incident_$timestamp$randomPart';
  }

  bool _isOffline(List<ConnectivityResult> results) {
    return results.isEmpty || results.contains(ConnectivityResult.none);
  }

  @override
  void dispose() {
    _playerStateSubscription?.cancel();
    _audioRecorder.dispose();
    _audioPlayer.dispose();
    super.dispose();
  }
}

class RequestServiceFormState {
  RequestServiceFormState({
    this.selectedVehicleId,
    this.inputMode = IncidentInputMode.text,
    this.description = '',
    this.audioPath,
    this.imagePaths = const [],
    this.isRecordingAudio = false,
    this.isAudioPaused = false,
    this.isPlayingAudio = false,
    this.isPosting = false,
    this.errorMessages = const [],
  });

  final String? selectedVehicleId;
  final IncidentInputMode inputMode;
  final String description;
  final String? audioPath;
  final List<String> imagePaths;
  final bool isRecordingAudio;
  final bool isAudioPaused;
  final bool isPlayingAudio;
  final bool isPosting;
  final List<String> errorMessages;

  bool get hasTextIncident => description.trim().isNotEmpty;
  bool get hasAudioIncident => (audioPath ?? '').trim().isNotEmpty;
  bool get hasIncident =>
      inputMode == IncidentInputMode.audio ? hasAudioIncident : hasTextIncident;
  bool get hasPhotos => imagePaths.isNotEmpty;
  bool get canSubmit =>
      selectedVehicleId != null && hasIncident && hasPhotos && !isPosting;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  RequestServiceFormState copyWith({
    Object? selectedVehicleId = _unset,
    IncidentInputMode? inputMode,
    String? description,
    Object? audioPath = _unset,
    List<String>? imagePaths,
    bool? isRecordingAudio,
    bool? isAudioPaused,
    bool? isPlayingAudio,
    bool? isPosting,
    List<String>? errorMessages,
  }) {
    return RequestServiceFormState(
      selectedVehicleId: selectedVehicleId == _unset
          ? this.selectedVehicleId
          : selectedVehicleId as String?,
      inputMode: inputMode ?? this.inputMode,
      description: description ?? this.description,
      audioPath: audioPath == _unset ? this.audioPath : audioPath as String?,
      imagePaths: imagePaths ?? this.imagePaths,
      isRecordingAudio: isRecordingAudio ?? this.isRecordingAudio,
      isAudioPaused: isAudioPaused ?? this.isAudioPaused,
      isPlayingAudio: isPlayingAudio ?? this.isPlayingAudio,
      isPosting: isPosting ?? this.isPosting,
      errorMessages: errorMessages ?? this.errorMessages,
    );
  }
}

const _unset = Object();
