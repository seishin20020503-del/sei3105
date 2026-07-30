"""Generate a Japanese-language improvement report from analysis results."""
from .efficiency import SegmentEfficiency
from .timing import TimingMatch


def _fmt_time(t: float) -> str:
    return f"{t:.2f}s"


def build_report(
    *,
    video_path: str,
    fps: float,
    duration_sec: float,
    left_segments: list[SegmentEfficiency],
    right_segments: list[SegmentEfficiency],
    timing_matches: list[TimingMatch] | None,
    top_n: int = 5,
    timing_ok_threshold_sec: float = 0.05,
) -> str:
    lines = []
    lines.append("# maimai 手の動き解析レポート")
    lines.append("")
    lines.append(f"- 対象動画: `{video_path}`")
    lines.append(f"- FPS: {fps:.1f} / 長さ: {duration_sec:.1f}秒")
    lines.append("")

    lines.append("## 手の移動効率")
    for label, segments in (("左手", left_segments), ("右手", right_segments)):
        lines.append(f"### {label}")
        if not segments:
            lines.append("（有効なタッチ区間が検出できませんでした）")
            lines.append("")
            continue
        worst = sorted(segments, key=lambda s: s.excess_distance, reverse=True)[:top_n]
        for s in worst:
            ratio = s.efficiency_ratio
            ratio_str = f"{ratio:.2f}倍" if ratio is not None else "N/A"
            lines.append(
                f"- {_fmt_time(s.from_event.time_sec)} → {_fmt_time(s.to_event.time_sec)}: "
                f"無駄な移動 {s.excess_distance:.0f}px"
                f"（実移動 {s.actual_distance:.0f}px / 最短 {s.straight_distance:.0f}px, {ratio_str}）"
            )
        lines.append("")

    if timing_matches is not None:
        lines.append("## タイミング分析")
        if not timing_matches:
            lines.append("（譜面とマッチするタッチが検出できませんでした）")
        else:
            deltas = [m.delta_sec for m in timing_matches]
            avg = sum(deltas) / len(deltas)
            early = sum(1 for d in deltas if d < -timing_ok_threshold_sec)
            late = sum(1 for d in deltas if d > timing_ok_threshold_sec)
            good = len(deltas) - early - late
            lines.append(f"- マッチ数: {len(deltas)} / 良好: {good} / 早押し: {early} / 遅れ: {late}")
            lines.append(f"- 平均ズレ: {avg * 1000:+.0f}ms（マイナス=早い, プラス=遅い）")
            worst_timing = sorted(timing_matches, key=lambda m: abs(m.delta_sec), reverse=True)[:top_n]
            lines.append("- ズレが大きいノーツ:")
            for m in worst_timing:
                sign = "早い" if m.delta_sec < 0 else "遅い"
                note_label = m.note.label or m.note.hand
                lines.append(f"  - {_fmt_time(m.note.time_sec)} ({note_label}): {abs(m.delta_sec) * 1000:.0f}ms {sign}")
        lines.append("")

    lines.append("## まとめ")
    suggestions = []
    for label, segments in (("左手", left_segments), ("右手", right_segments)):
        if segments:
            worst_one = max(segments, key=lambda s: s.excess_distance, default=None)
            if worst_one is not None and worst_one.excess_distance > 0:
                suggestions.append(
                    f"- {label}: {_fmt_time(worst_one.from_event.time_sec)}付近の移動に無駄が見られます。"
                    "最短経路を意識してみましょう。"
                )
    if timing_matches:
        avg = sum(m.delta_sec for m in timing_matches) / len(timing_matches)
        if avg < -timing_ok_threshold_sec:
            suggestions.append(f"- 全体的に平均{abs(avg) * 1000:.0f}ms早押しの傾向があります。少し我慢して合わせてみましょう。")
        elif avg > timing_ok_threshold_sec:
            suggestions.append(f"- 全体的に平均{avg * 1000:.0f}ms遅れの傾向があります。もう少し早めを意識してみましょう。")
    if not suggestions:
        suggestions.append("- 大きな改善点は検出されませんでした。")
    lines.extend(suggestions)

    return "\n".join(lines)
