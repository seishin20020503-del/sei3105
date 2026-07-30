import SwiftUI
import PhotosUI
import UniformTypeIdentifiers

/// Wraps `PHPickerViewController`, filtered to videos only, and copies the
/// picked movie into the app's temporary directory so it can be opened by
/// `AVAsset` after the picker (and its out-of-process extension) is dismissed.
struct VideoPicker: UIViewControllerRepresentable {
    var onPick: (URL) -> Void
    var onFailure: (String) -> Void

    func makeUIViewController(context: Context) -> PHPickerViewController {
        var configuration = PHPickerConfiguration(photoLibrary: .shared())
        configuration.filter = .videos
        configuration.selectionLimit = 1

        let picker = PHPickerViewController(configuration: configuration)
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ uiViewController: PHPickerViewController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(onPick: onPick, onFailure: onFailure)
    }

    final class Coordinator: NSObject, PHPickerViewControllerDelegate {
        private let onPick: (URL) -> Void
        private let onFailure: (String) -> Void

        init(onPick: @escaping (URL) -> Void, onFailure: @escaping (String) -> Void) {
            self.onPick = onPick
            self.onFailure = onFailure
        }

        func picker(_ picker: PHPickerViewController, didFinishPicking results: [PHPickerResult]) {
            picker.dismiss(animated: true)

            guard let provider = results.first?.itemProvider,
                  provider.hasItemConformingToTypeIdentifier(UTType.movie.identifier) else {
                return
            }

            provider.loadFileRepresentation(forTypeIdentifier: UTType.movie.identifier) { [onPick, onFailure] url, error in
                guard let url else {
                    let message = error?.localizedDescription ?? "動画の読み込みに失敗しました。"
                    DispatchQueue.main.async { onFailure(message) }
                    return
                }

                let destination = FileManager.default.temporaryDirectory
                    .appendingPathComponent(UUID().uuidString)
                    .appendingPathExtension(url.pathExtension.isEmpty ? "mov" : url.pathExtension)

                do {
                    if FileManager.default.fileExists(atPath: destination.path) {
                        try FileManager.default.removeItem(at: destination)
                    }
                    try FileManager.default.copyItem(at: url, to: destination)
                    DispatchQueue.main.async { onPick(destination) }
                } catch {
                    DispatchQueue.main.async {
                        onFailure("動画の読み込みに失敗しました: \(error.localizedDescription)")
                    }
                }
            }
        }
    }
}
