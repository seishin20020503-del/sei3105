import SwiftUI

struct ContentView: View {
    @State private var isPickerPresented = false
    @State private var selectedVideoURL: URL?
    @State private var pickerErrorMessage: String?

    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                Spacer()

                Image(systemName: "film.stack")
                    .font(.system(size: 64))
                    .foregroundStyle(.tint)

                Text("動画をコマ送りで確認")
                    .font(.title2.bold())

                Text("ライブラリから動画を選ぶと、1フレームずつ、または2コマ・3コマおきに送りながら再生できます。")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 32)

                if let pickerErrorMessage {
                    Text(pickerErrorMessage)
                        .font(.footnote)
                        .foregroundStyle(.red)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 32)
                }

                Spacer()

                Button {
                    isPickerPresented = true
                } label: {
                    Label("動画を選択", systemImage: "photo.on.rectangle")
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
                .padding(.horizontal)
                .padding(.bottom, 32)
            }
            .navigationTitle("FrameStep")
            .sheet(isPresented: $isPickerPresented) {
                VideoPicker(
                    onPick: { url in
                        pickerErrorMessage = nil
                        selectedVideoURL = url
                    },
                    onFailure: { message in
                        pickerErrorMessage = message
                    }
                )
            }
            .navigationDestination(item: $selectedVideoURL) { url in
                FramePlayerView(videoURL: url)
            }
        }
    }
}

#Preview {
    ContentView()
}
