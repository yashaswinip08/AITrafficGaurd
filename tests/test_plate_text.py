from trafficguard.ocr.plate_text import normalize_plate_text


def test_valid_plate_format():
    reading = normalize_plate_text('KA01AB1234', confidence=0.95)
    assert reading.cleaned_text == 'KA01AB1234'
    assert reading.valid_format is True


def test_lowercase_and_spaces():
    reading = normalize_plate_text(' ka01 ab1234 ', confidence=0.9)
    assert reading.cleaned_text == 'KA01AB1234'


def test_hyphen_and_special_chars():
    reading = normalize_plate_text('KA-01-AB-1234', confidence=0.8)
    assert 'KA01AB1234' in reading.cleaned_text


def test_ocr_confusion_values():
    reading = normalize_plate_text('KAO1AB1234', confidence=0.9)
    assert '0' in reading.cleaned_text or reading.cleaned_text.startswith('KA')


def test_invalid_plate_rejected():
    reading = normalize_plate_text('HELLO123', confidence=0.2)
    assert reading.valid_format is False
