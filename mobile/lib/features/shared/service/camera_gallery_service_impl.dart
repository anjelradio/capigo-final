import 'package:image_picker/image_picker.dart';
import 'service.dart';

class CameraGalleryServiceImpl extends CameraGalleryService {
  final ImagePicker _picker = ImagePicker();

  @override
  Future<String?> selectPhoto() async {
    final XFile? photo = await _picker.pickImage(
      source: ImageSource.gallery,
      imageQuality: 80,
    );

    if (photo == null) return null;

    print('Tenemos una imagen ${photo.path}');
    return photo.path;
  }

  @override
  Future<List<String>> selectPhotos() async {
    final photos = await _picker.pickMultiImage(imageQuality: 80);
    if (photos.isEmpty) return const [];

    return photos.map((photo) => photo.path).toList();
  }

  @override
  Future<String?> takePhoto() async {
    final XFile? photo = await _picker.pickImage(
      source: ImageSource.camera,
      imageQuality: 80,
      preferredCameraDevice: CameraDevice.rear,
    );

    if (photo == null) return null;

    print('Tenemos una imagen ${photo.path}');
    return photo.path;
  }
}
