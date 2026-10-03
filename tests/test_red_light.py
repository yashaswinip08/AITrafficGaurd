import numpy as np

from trafficguard.rules.red_light import RedLightRule


class DummyTrack:
    def __init__(self, track_id, class_name, bbox):
        self.track_id = track_id
        self.class_name = class_name
        self.bbox = bbox


def test_red_light_crossing_triggers_violation():
    rule = RedLightRule({
        'traffic_light': {'roi': {'x1': 0, 'y1': 0, 'x2': 100, 'y2': 100}},
        'stop_line': {'points': [[0, 50], [100, 50]]},
    })
    frame = np.full((100, 100, 3), (0, 0, 255), dtype=np.uint8)
    track = DummyTrack(7, 'car', (40, 60, 80, 90))
    violations = rule.check({'frame': frame, 'tracks': [track], 'frame_index': 10, 'timestamp': '2026-10-03T00:00:00', 'camera_id': 'cam_01'})
    assert len(violations) == 1
    assert violations[0].violation_type == 'red_light'


def test_green_light_no_violation():
    rule = RedLightRule({
        'traffic_light': {'roi': {'x1': 0, 'y1': 0, 'x2': 100, 'y2': 100}},
        'stop_line': {'points': [[0, 50], [100, 50]]},
    })
    frame = np.full((100, 100, 3), (0, 255, 0), dtype=np.uint8)
    track = DummyTrack(8, 'car', (40, 60, 80, 90))
    assert rule.check({'frame': frame, 'tracks': [track], 'frame_index': 11, 'timestamp': '2026-10-03T00:00:00', 'camera_id': 'cam_01'}) == []
