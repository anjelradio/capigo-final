import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:path_provider/path_provider.dart';

import 'package:mobile/features/auth/data/errors/auth_errors.dart';
import 'package:mobile/features/incidents/data/repositories/incident_repository.dart';

import 'offline_incident_submission.dart';

class IncidentOfflineQueueService {
  static const String _boxName = 'incident_offline_queue';
  static const String _attachmentsFolderName = 'incident_offline_attachments';

  final Connectivity _connectivity = Connectivity();
  final Random _random = Random();

  Box<String>? _box;
  Future<IncidentRepository> Function()? _repositoryResolver;
  bool Function()? _canSync;
  StreamSubscription<List<ConnectivityResult>>? _connectivitySubscription;
  bool _isSyncing = false;

  Future<void> start({
    required Future<IncidentRepository> Function() repositoryResolver,
    bool Function()? canSync,
  }) async {
    _repositoryResolver = repositoryResolver;
    _canSync = canSync;
    await _ensureBox();

    _connectivitySubscription ??= _connectivity.onConnectivityChanged.listen((results) {
      if (_hasConnection(results)) {
        unawaited(syncPending());
      }
    });

    if (_canSync == null || _canSync!()) {
      unawaited(syncPending());
    }
  }

  Future<void> stop() async {
    await _connectivitySubscription?.cancel();
    _connectivitySubscription = null;
  }

  Future<OfflineIncidentSubmission> enqueueIncident({
    required String vehicleId,
    String? description,
    String? audioPath,
    required double latitude,
    required double longitude,
    required List<String> imagePaths,
    String? clientRequestId,
  }) async {
    final box = await _ensureBox();
    final requestId = (clientRequestId?.trim().isNotEmpty == true)
        ? clientRequestId!.trim()
        : _generateClientRequestId();

    try {
      final persistedImagePaths = <String>[];
      for (var index = 0; index < imagePaths.length; index++) {
        persistedImagePaths.add(
          await _copyAttachmentToPersistentStorage(
            sourcePath: imagePaths[index],
            clientRequestId: requestId,
            kind: 'image',
            index: index,
          ),
        );
      }

      final persistedAudioPath = audioPath == null || audioPath.trim().isEmpty
          ? null
          : await _copyAttachmentToPersistentStorage(
              sourcePath: audioPath,
              clientRequestId: requestId,
              kind: 'audio',
              index: 0,
            );

      final submission = OfflineIncidentSubmission(
        clientRequestId: requestId,
        vehicleId: vehicleId,
        description: description,
        audioPath: persistedAudioPath,
        imagePaths: persistedImagePaths,
        latitude: latitude,
        longitude: longitude,
        createdAt: DateTime.now().toUtc(),
      );

      await box.put(requestId, jsonEncode(submission.toJson()));
      return submission;
    } catch (_) {
      await _deleteAttachmentFolder(requestId);
      rethrow;
    }
  }

  Future<List<OfflineIncidentSubmission>> getPendingIncidents() async {
    final box = await _ensureBox();
    final pending = box.values
        .map((raw) {
          final decoded = jsonDecode(raw);
          if (decoded is! Map<String, dynamic>) {
            return null;
          }
          return OfflineIncidentSubmission.fromJson(decoded);
        })
        .whereType<OfflineIncidentSubmission>()
        .toList();

    pending.sort((left, right) => left.createdAt.compareTo(right.createdAt));
    return pending;
  }

  Future<void> syncPending() async {
    if (_isSyncing) return;

    final repositoryResolver = _repositoryResolver;
    if (repositoryResolver == null) return;
    final canSync = _canSync;
    if (canSync != null && !canSync()) return;

    final connectivity = await _connectivity.checkConnectivity();
    if (!_hasConnection(connectivity)) return;

    _isSyncing = true;
    try {
      final repository = await repositoryResolver();
      final pending = await getPendingIncidents();

      for (final submission in pending) {
        final currentConnectivity = await _connectivity.checkConnectivity();
        if (!_hasConnection(currentConnectivity)) {
          break;
        }

        try {
          await repository.createIncident(
            vehicleId: submission.vehicleId,
            description: submission.description,
            audioPath: submission.audioPath,
            latitude: submission.latitude,
            longitude: submission.longitude,
            imagePaths: submission.imagePaths,
            clientRequestId: submission.clientRequestId,
          );
          await removePendingIncident(submission.clientRequestId);
        } on CustomError {
          break;
        } catch (_) {
          break;
        }
      }
    } finally {
      _isSyncing = false;
    }
  }

  Future<void> removePendingIncident(String clientRequestId) async {
    final box = await _ensureBox();
    await box.delete(clientRequestId);
    await _deleteAttachmentFolder(clientRequestId);
  }

  Future<Box<String>> _ensureBox() async {
    final existing = _box;
    if (existing != null) return existing;

    final box = await Hive.openBox<String>(_boxName);
    _box = box;
    return box;
  }

  bool _hasConnection(List<ConnectivityResult> results) {
    return results.isNotEmpty && !results.contains(ConnectivityResult.none);
  }

  String _generateClientRequestId() {
    final timestamp = DateTime.now().toUtc().microsecondsSinceEpoch.toRadixString(36);
    final randomPart = _random.nextInt(1 << 32).toRadixString(36);
    return 'incident_$timestamp$randomPart';
  }

  Future<String> _copyAttachmentToPersistentStorage({
    required String sourcePath,
    required String clientRequestId,
    required String kind,
    required int index,
  }) async {
    final sourceFile = File(sourcePath);
    if (!await sourceFile.exists()) {
      throw CustomError('No fue posible guardar un archivo temporal del incidente');
    }

    final baseDirectory = await getApplicationDocumentsDirectory();
    final targetDirectory = Directory(
      '${baseDirectory.path}/$_attachmentsFolderName/$clientRequestId',
    );
    await targetDirectory.create(recursive: true);

    final extension = _extractExtension(sourcePath);
    final destinationPath = '${targetDirectory.path}/${kind}_$index$extension';
    final copiedFile = await sourceFile.copy(destinationPath);
    return copiedFile.path;
  }

  Future<void> _deleteAttachmentFolder(String clientRequestId) async {
    final baseDirectory = await getApplicationDocumentsDirectory();
    final targetDirectory = Directory(
      '${baseDirectory.path}/$_attachmentsFolderName/$clientRequestId',
    );
    if (await targetDirectory.exists()) {
      await targetDirectory.delete(recursive: true);
    }
  }

  String _extractExtension(String sourcePath) {
    final fileName = sourcePath.split(Platform.pathSeparator).last;
    final dotIndex = fileName.lastIndexOf('.');
    if (dotIndex == -1) return '';
    return fileName.substring(dotIndex);
  }
}
