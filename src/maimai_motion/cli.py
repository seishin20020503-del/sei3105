"""Command-line entry point: analyze a maimai gameplay video and report
hand-movement improvement points.
"""
import argparse
import sys

from .chart import load_chart
from .efficiency import compute_segment_efficiencies
from .hand_tracker import extract_hand_trajectories
from .report import build_report
from .timing import match_notes_to_touches
from .touch_detection import detect_touch_events
from .trajectory import reference_trajectory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="maimai gameplay video hand-motion analyzer")
    parser.add_argument("video", help="path to gameplay video")
    parser.add_argument("--chart", help="path to JSON note chart for timing analysis")
    parser.add_argument("--out", default="report.md", help="output report path (markdown)")
    parser.add_argument(
        "--landmark",
        type=int,
        default=0,
        help="MediaPipe hand landmark index used as the reference point (0=wrist, 8=index fingertip)",
    )
    parser.add_argument(
        "--speed-threshold",
        type=float,
        default=40.0,
        help="pixels/sec below which the hand is considered still (i.e. touching)",
    )
    parser.add_argument("--timing-window", type=float, default=0.5, help="max seconds to match a touch to a note")
    parser.add_argument("--timing-ok", type=float, default=0.05, help="seconds within which timing is considered good")
    parser.add_argument("--top-n", type=int, default=5, help="number of worst items to list per section")
    parser.add_argument("--mirror", action="store_true", help="swap left/right hand labels (use if camera view is mirrored)")
    parser.add_argument("--plot-left", help="save left-hand trajectory plot to this path")
    parser.add_argument("--plot-right", help="save right-hand trajectory plot to this path")
    args = parser.parse_args(argv)

    data = extract_hand_trajectories(args.video, mirror=args.mirror)
    duration_sec = max(len(data.left), len(data.right), 1) / data.fps

    left_times, left_pos = reference_trajectory(data.left, args.landmark, data.width, data.height)
    right_times, right_pos = reference_trajectory(data.right, args.landmark, data.width, data.height)

    left_events = detect_touch_events(left_times, left_pos, args.speed_threshold)
    right_events = detect_touch_events(right_times, right_pos, args.speed_threshold)

    left_segments = compute_segment_efficiencies(left_times, left_pos, left_events)
    right_segments = compute_segment_efficiencies(right_times, right_pos, right_events)

    timing_matches = None
    if args.chart:
        notes = load_chart(args.chart)
        left_notes = [n for n in notes if n.hand in ("left", "either")]
        right_notes = [n for n in notes if n.hand in ("right", "either")]
        timing_matches = match_notes_to_touches(
            left_notes, left_events, args.timing_window
        ) + match_notes_to_touches(right_notes, right_events, args.timing_window)

    report = build_report(
        video_path=args.video,
        fps=data.fps,
        duration_sec=duration_sec,
        left_segments=left_segments,
        right_segments=right_segments,
        timing_matches=timing_matches,
        top_n=args.top_n,
        timing_ok_threshold_sec=args.timing_ok,
    )

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)

    if args.plot_left and left_times:
        from .visualize import plot_trajectory

        plot_trajectory(left_times, left_pos, left_events, args.plot_left, title="Left hand")
    if args.plot_right and right_times:
        from .visualize import plot_trajectory

        plot_trajectory(right_times, right_pos, right_events, args.plot_right, title="Right hand")

    return 0


if __name__ == "__main__":
    sys.exit(main())
