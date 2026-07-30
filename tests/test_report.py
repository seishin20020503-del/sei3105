from maimai_motion.chart import Note
from maimai_motion.efficiency import SegmentEfficiency
from maimai_motion.report import build_report
from maimai_motion.timing import TimingMatch
from maimai_motion.touch_detection import TouchEvent


def _event(t, pos=(0.0, 0.0)):
    return TouchEvent(time_sec=t, position=pos, start_frame_pos=0, end_frame_pos=0)


def test_build_report_includes_all_sections():
    left_segments = [SegmentEfficiency(_event(0.0), _event(1.0), straight_distance=10.0, actual_distance=20.0)]
    right_segments = []
    timing_matches = [
        TimingMatch(note=Note(time_sec=1.0, hand="left", label="tap"), touch=_event(1.08)),
    ]

    report = build_report(
        video_path="video.mp4",
        fps=30.0,
        duration_sec=12.3,
        left_segments=left_segments,
        right_segments=right_segments,
        timing_matches=timing_matches,
    )

    assert "maimai 手の動き解析レポート" in report
    assert "video.mp4" in report
    assert "無駄な移動 10px" in report
    assert "タイミング分析" in report
    assert "早押し" in report
    assert "まとめ" in report


def test_build_report_handles_empty_data():
    report = build_report(
        video_path="video.mp4",
        fps=30.0,
        duration_sec=0.0,
        left_segments=[],
        right_segments=[],
        timing_matches=None,
    )
    assert "有効なタッチ区間が検出できませんでした" in report
    assert "タイミング分析" not in report
    assert "大きな改善点は検出されませんでした" in report
