import Foundation
import AVFoundation
import CoreMedia
import UIKit

/// Drives frame-accurate stepping through a video: normal playback via
/// `AVPlayer`, and exact single-frame stills (for stepping / scrubbing) via
/// `AVAssetImageGenerator` with zero time tolerance.
///
/// Many real-world sources (iOS screen recordings in particular) are encoded
/// with a variable frame rate: the container reports a nominal rate like
/// 60fps, but individual frames are not spaced at exactly 1/60s apart. A
/// naive `index / nominalFrameRate` mapping drifts off the real frame
/// boundaries on that kind of file, so stepping "1 frame" can skip or repeat
/// a frame. To stay exact regardless of source, this loads every frame's
/// real presentation timestamp once (via `AVAssetReader`) and steps through
/// that timeline instead of a computed constant frame duration.
@MainActor
final class FramePlayerViewModel: ObservableObject {
    @Published private(set) var currentImage: UIImage?
    @Published private(set) var currentFrameIndex: Int = 0
    @Published private(set) var isPlaying = false
    @Published private(set) var isRefiningFrameTimeline = true
    @Published var stepSize: Int = 1

    let player: AVPlayer
    private(set) var totalFrames: Int
    let duration: CMTime

    private let asset: AVAsset
    private let videoTrack: AVAssetTrack
    private let approximateFrameRate: Double
    private let imageGenerator: AVAssetImageGenerator
    private var timeObserverToken: Any?

    /// Exact presentation timestamp of every video sample, sorted ascending.
    /// Empty until `loadExactFrameTimeline()` finishes; until then frame
    /// positions fall back to the constant-frame-rate approximation.
    private var frameTimes: [CMTime] = []

    init?(url: URL) {
        let asset = AVURLAsset(url: url)
        guard let track = asset.tracks(withMediaType: .video).first,
              track.nominalFrameRate > 0 else {
            return nil
        }

        let approximateFrameRate = Double(track.nominalFrameRate)
        self.asset = asset
        self.videoTrack = track
        self.approximateFrameRate = approximateFrameRate
        self.duration = asset.duration
        self.totalFrames = max(1, Int((asset.duration.seconds * approximateFrameRate).rounded()))

        let generator = AVAssetImageGenerator(asset: asset)
        generator.appliesPreferredTrackTransform = true
        generator.requestedTimeToleranceBefore = .zero
        generator.requestedTimeToleranceAfter = .zero
        self.imageGenerator = generator

        self.player = AVPlayer(playerItem: AVPlayerItem(asset: asset))

        let interval = CMTime(seconds: 1.0 / approximateFrameRate, preferredTimescale: 600)
        timeObserverToken = player.addPeriodicTimeObserver(forInterval: interval, queue: .main) { [weak self] time in
            guard let self else { return }
            self.currentFrameIndex = self.nearestFrameIndex(forTime: time.seconds)
            if time.seconds >= self.duration.seconds - (1.0 / self.approximateFrameRate) {
                self.pause()
            }
        }

        Task {
            await showFrame(at: 0)
            await loadExactFrameTimeline()
        }
    }

    deinit {
        if let token = timeObserverToken {
            player.removeTimeObserver(token)
        }
    }

    /// Reads every video sample's real presentation timestamp off the main
    /// actor so 1-frame stepping lands exactly on encoded frame boundaries,
    /// even for variable-frame-rate sources.
    private func loadExactFrameTimeline() async {
        let asset = asset
        let track = videoTrack

        let times = await Task.detached(priority: .userInitiated) { () -> [CMTime]? in
            guard let reader = try? AVAssetReader(asset: asset) else { return nil }
            let output = AVAssetReaderTrackOutput(track: track, outputSettings: nil)
            output.alwaysCopiesSampleData = false
            guard reader.canAdd(output) else { return nil }
            reader.add(output)
            guard reader.startReading() else { return nil }

            var collected: [CMTime] = []
            while let sampleBuffer = output.copyNextSampleBuffer() {
                let pts = CMSampleBufferGetPresentationTimeStamp(sampleBuffer)
                if pts.isValid {
                    collected.append(pts)
                }
            }
            return collected.sorted { $0.seconds < $1.seconds }
        }.value

        guard let times, !times.isEmpty else {
            isRefiningFrameTimeline = false
            return
        }

        frameTimes = times
        totalFrames = times.count
        isRefiningFrameTimeline = false

        if !isPlaying {
            await showFrame(at: currentFrameIndex)
        }
    }

    private func nearestFrameIndex(forTime seconds: Double) -> Int {
        guard !frameTimes.isEmpty else {
            return max(0, min(totalFrames - 1, Int((seconds * approximateFrameRate).rounded())))
        }

        var low = 0
        var high = frameTimes.count - 1
        while low < high {
            let mid = (low + high) / 2
            if frameTimes[mid].seconds < seconds {
                low = mid + 1
            } else {
                high = mid
            }
        }
        if low > 0, abs(frameTimes[low - 1].seconds - seconds) <= abs(frameTimes[low].seconds - seconds) {
            return low - 1
        }
        return low
    }

    func frameTime(_ index: Int) -> CMTime {
        let clamped = max(0, min(index, totalFrames - 1))
        if frameTimes.indices.contains(clamped) {
            return frameTimes[clamped]
        }
        let seconds = min(Double(clamped) / approximateFrameRate, duration.seconds)
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
