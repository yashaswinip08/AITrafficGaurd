from trafficguard.analysis import analyze_vehicle_input, pick_best_plate


def test_pick_best_plate_prefers_valid_indian_plate():
    best = pick_best_plate(["unknown", "KA-01-AB-1234", "HELLO123"])
    assert best.cleaned_text == "KA01AB1234"
    assert best.valid_format is True


def test_analyze_vehicle_input_uses_ocr_and_violation_type():
    analysis = analyze_vehicle_input("KA 01 AB 1234", violation_type="red_light")
    assert analysis["plate"] == "KA01AB1234"
    assert analysis["violation_type"] == "red_light"
    assert analysis["status"] == "ready"
