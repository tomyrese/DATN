import time
from src.config import RobotConfig
from src.network.pairing_manager import PairingManager

def test_pairing_code_generation():
    cfg = RobotConfig(PAIRING_CODE_TTL=120.0, SERVER_PORT=8765)
    pm = PairingManager(cfg)

    code, payload = pm.start_pairing(host="192.168.1.50", port=8765)
    assert len(code) == 6
    assert code.isalnum()
    assert payload == f"http://192.168.1.50:8765/?code={code}"
    assert pm.is_pairing_active()
    assert pm.get_remaining_seconds() > 0

def test_pairing_validation_success():
    cfg = RobotConfig(PAIRING_CODE_TTL=120.0)
    pm = PairingManager(cfg)
    code, _ = pm.start_pairing()

    assert pm.validate_code(code)
    assert not pm.is_pairing_active()

def test_pairing_validation_invalid_code():
    cfg = RobotConfig(PAIRING_CODE_TTL=120.0)
    pm = PairingManager(cfg)
    pm.start_pairing()

    assert not pm.validate_code("WRONG1")
    assert pm.is_pairing_active()

def test_pairing_expiration():
    cfg = RobotConfig(PAIRING_CODE_TTL=0.05)
    pm = PairingManager(cfg)
    code, _ = pm.start_pairing()

    time.sleep(0.08)
    assert not pm.is_pairing_active()
    assert not pm.validate_code(code)

def test_qr_image_generation():
    cfg = RobotConfig()
    pm = PairingManager(cfg)
    pm.start_pairing()

    qr_img = pm.generate_qr_image(56)
    assert qr_img is not None
    assert qr_img.size[0] >= 40
    assert qr_img.size[1] >= 40
    assert qr_img.mode == "1"
