import json

from maimai_motion.chart import load_chart


def test_load_chart_sorts_and_fills_defaults(tmp_path):
    chart_path = tmp_path / "chart.json"
    chart_path.write_text(
        json.dumps(
            [
                {"time": 2.0, "hand": "right", "label": "tap2"},
                {"time": 1.0, "hand": "left"},
            ]
        ),
        encoding="utf-8",
    )
    notes = load_chart(str(chart_path))
    assert [n.time_sec for n in notes] == [1.0, 2.0]
    assert notes[0].hand == "left"
    assert notes[0].label == ""
    assert notes[1].label == "tap2"


def test_load_chart_defaults_hand_to_either(tmp_path):
    chart_path = tmp_path / "chart.json"
    chart_path.write_text(json.dumps([{"time": 0.5}]), encoding="utf-8")
    notes = load_chart(str(chart_path))
    assert notes[0].hand == "either"
