from trafficguard.rules.base import Violation


def test_deduplication_key_generator():
    v1 = Violation(violation_type='red_light', vehicle_class='car', track_id=5, plate_text='KA01AB1234')
    v2 = Violation(violation_type='red_light', vehicle_class='car', track_id=5, plate_text='KA01AB1234')
    assert v1.to_record()['violation_type'] == 'red_light'
    assert v2.to_record()['track_id'] == 5
