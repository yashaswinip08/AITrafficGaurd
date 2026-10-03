from trafficguard.rules.no_helmet import NoHelmetRule


class DummyTrack:
    def __init__(self, track_id, class_name):
        self.track_id = track_id
        self.class_name = class_name


class DummyDetector:
    def detect(self, frame, detections):
        return [{"no_helmet": True, "confidence": 0.9}]


def test_motorcycle_no_helmet_rule():
    rule = NoHelmetRule(DummyDetector())
    track = DummyTrack(1, 'motorcycle')
    violations = rule.check({'frame': None, 'tracks': [track], 'frame_index': 1, 'timestamp': 't', 'camera_id': 'cam_01'})
    assert len(violations) == 1
    assert violations[0].violation_type == 'no_helmet'


def test_car_is_ignored():
    rule = NoHelmetRule(DummyDetector())
    track = DummyTrack(2, 'car')
    assert rule.check({'frame': None, 'tracks': [track], 'frame_index': 1, 'timestamp': 't', 'camera_id': 'cam_01'}) == []


def test_missing_detector_is_safe():
    rule = NoHelmetRule(None)
    track = DummyTrack(3, 'motorcycle')
    assert rule.check({'frame': None, 'tracks': [track], 'frame_index': 1, 'timestamp': 't', 'camera_id': 'cam_01'}) == []
