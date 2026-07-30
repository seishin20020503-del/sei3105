import SwiftUI
import AVFoundation

struct FramePlayerView: View {
    @StateObject private var loader: FramePlayerLoader

    init(videoURL: URL) {
        _loader = StateObject(wrappedValue: FramePlayerLoader(url: videoURL))
    }

    var body: some View {
        Group {
            if let viewModel = loader.viewModel {
                FramePlayerContentView(viewModel: viewModel)
            } else {
                ContentUnavailableFallbackView()
            }
        }
    }
}

/// Owns the (possibly nil) view model so `FramePlayerView` can present a
/// friendly fallback if the picked file turns out not to be a readable video.
@MainActor
final class FramePlayerLoader: ObservableObject {
    let viewModel: FramePlayerViewModel?

    init(url: URL) {
        viewModel = FramePlayerViewModel(url: url)
    }
}

private struct ContentUnavailableFallbackView: View {
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 40))
                .foregroundStyle(.secondary)
            Text("この動画は読み込めませんでした。")
                .font(.headline)
            Text("別の動画を選んでもう一度お試しください。")
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
        .padding()
        .navigationTitle("フレームプレイヤー")
        .navigationBarTitleDisplayMode(.inline)
    }
}

private struct FramePlayerContentView: View {
    @ObservedObject var viewModel: FramePlayerViewModel

    var body: some View {
        VStack(spacing: 16) {
            ZStack {
                Color.black
                if viewModel.isPlaying {
                    PlayerLayerView(player: viewModel.player)
                } else if let image = viewModel.currentImage {
                    Image(uiImage: image)
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                }
            }
            .aspectRatio(16.0 / 9.0, contentMode: .fit)
            .clipShape(RoundedRectangle(cornerRadius: 12))
            .padding(.horizontal)
            .padding(.top)

            Text("フレーム \(viewModel.currentFrameIndex + 1) / \(viewModel.totalFrames)")
                .font(.subheadline.monospacedDigit())
                .foregroundStyle(.secondary)

            if viewModel.isRefiningFrameTimeline {
                Label("正確なフレーム位置を解析中…", systemImage: "gearshape.arrow.triangle.2.circlepath")
                    .font(.caption)
                    .foregroundStyle(.tertiary)
            }

            Slider(
                value: Binding(
                    get: { Double(viewModel.currentFrameIndex) },
                    set: { viewModel.scrub(toFrame: Int($0.rounded())) }
                ),
                in: 0...Double(max(viewModel.totalFrames - 1, 1)),
                step: 1
            )
            .padding(.horizontal)

            VStack(spacing: 8) {
                Text("コマ送り幅")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Picker("コマ送り幅", selection: $viewModel.stepSize) {
                    Text("1コマ").tag(1)
                    Text("2コマおき").tag(2)
                    Text("3コマおき").tag(3)
                }
                .pickerStyle(.segmented)
            }
            .padding(.horizontal)

            HStack(spacing: 40) {
                Button {
                    viewModel.stepBackward()
                } label: {
                    Image(systemName: "backward.frame.fill")
                        .font(.system(size: 30))
                }

                Button {
                    viewModel.togglePlayback()
                } label: {
                    Image(systemName: viewModel.isPlaying ? "pause.circle.fill" : "play.circle.fill")
                        .font(.system(size: 50))
                }

                Button {
                    viewModel.stepForward()
                } label: {
                    Image(systemName: "forward.frame.fill")
                        .font(.system(size: 30))
                }
            }
            .padding(.vertical, 8)

            Spacer(minLength: 0)
        }
        .navigationTitle("フレームプレイヤー")
        .navigationBarTitleDisplayMode(.inline)
    }
}

private struct PlayerLayerView: UIViewRepresentable {
    let player: AVPlayer

    func makeUIView(context: Context) -> PlayerContainerView {
        let view = PlayerContainerView()
        view.playerLayer.player = player
        view.playerLayer.videoGravity = .resizeAspect
        return view
    }

    func updateUIView(_ uiView: PlayerContainerView, context: Context) {
        uiView.playerLayer.player = player
    }
}

private final class PlayerContainerView: UIView {
    override static var layerClass: AnyClass { AVPlayerLayer.self }

    var playerLayer: AVPlayerLayer {
        // swiftlint:disable:next force_cast
        layer as! AVPlayerLayer
    }
}
