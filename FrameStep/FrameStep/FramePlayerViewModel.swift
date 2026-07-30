import Foundation
import AVFoundation
import UIKit

/// Drives frame-accurate stepping through a video: normal playback via
/// `AVPlayer`, and exact single-frame stills (for stepping / scrubbing) via
/// `AVAssetImageGenerator` with zero time tolerance.
@MainActor
final class FramePlayerViewModel: ObservableObject {
    @Published private(set) var currentImage: UIImage?
    @Published private(set) var currentFrameIndex: Int = 0
    @Published private(set) var isPlaying = false
    @Published var stepSize: Int = 1

    let player: AVPlayer
    let totalFrames: Int
    let frameRate: Double
    let duration: CMTime

    private let asset: AVAsset
    private let imageGenerator: AVAssetImageGenerator
    private var timeObserverToken: Any?

    init?(url: URL) {
        let asset = AVURLAsset(url: url)
        guard let track = asset.tracks(withMediaType: .video).first,
              track.nominalFrameRate > 0 else {
            return nil
        }

        let frameRate = Double(track.nominalFrameRate)
        self.asset = asset
        self.frameRate = frameRate
        self.duration = asset.duration
        self.totalFrames = max(1, Int((asset.duration.seconds * frameRate).rounded()))

        let generator = AVAssetImageGenerator(asset: asset)
        generator.appliesPreferredTrackTransform = true
        generator.requestedTimeToleranceBefore = .zero
        generator.requestedTimeToleranceAfter = .zero
        self.imageGenerator = generator

        self.player = AVPlayer(playerItem: AVPlayerItem(asset: asset))

        let interval = CMTime(seconds: 1.0 / frameRate, preferredTimescale: 600)
        timeObserverToken = player.addPeriodicTimeObserver(forInterval: interval, queue: .main) { [weak self] time in
            guard let self else { return }
            self.currentFrameIndex = min(self.totalFrames - 1, Int((time.seconds * self.frameRate).rounded()))
            if time.seconds >= self.duration.seconds - (1.0 / self.frameRate) {
                self.pause()
            }
        }

        Task { await showFrame(at: 0) }
    }

    deinit {
        if let token = timeObserverToken {
            player.removeTimeObserver(token)
        }
    }

    func frameTime(_ index: Int) -> CMTime {
        let seconds = min(Double(index) / frameRate, duration.seconds)
        return CMTime(seconds: seconds, preferredTimescale: 600)
    }

    /// Renders the exact still image for `index` and syncs the (paused) player to match.
    func showFrame(at index: Int) async {
        let clamped = max(0, min(index, totalFrames - 1))
        let time = frameTime(clamped)
        currentFrameIndex = clamped

        if let result = try? await imageGenerator.image(at: time) {
            currentImage = UIImage(cgImage: result.image)
        }

        await player.seek(to: time, toleranceBefore: .zero, toleranceAfter: .zero)
    }

    func stepForward() { moveFrames(by: stepSize) }
    func stepBackward() { moveFrames(by: -stepSize) }

    private func moveFrames(by amount: Int) {
        pause()
        Task { await showFrame(at: currentFrameIndex + amount) }
    }

    func scrub(toFrame index: Int) {
        pause()
        Task { await showFrame(at: index) }
    }

    func togglePlayback() {
        isPlaying ? pause() : play()
    }

    func play() {
        let startFromBeginning = currentFrameIndex >= totalFrames - 1
        isPlaying = true
        Task {
            if startFromBeginning {
                await showFrame(at: 0)
            }
            player.play()
        }
    }

    func pause() {
        guard isPlaying || player.rate != 0 else { return }
        player.pause()
        isPlaying = false
        Task { await showFrame(at: currentFrameIndex) }
    }
}
