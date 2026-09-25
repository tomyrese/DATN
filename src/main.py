import sys
import os
import time
import signal
from pathlib import Path

# Ensure project root is in sys.path so 'src' can be imported from anywhere
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import config
from src.state import MovementCommand
from src.services.robot_controller import RobotController
from src.services.logging_service import logger

def get_key_reader():
    if os.name == "nt":
        import msvcrt
        def read_key():
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                try:
                    return ch.decode("utf-8").lower()
                except UnicodeDecodeError:
                    return ""
            return None
        return read_key
    else:
        import select
        if not sys.stdin.isatty():
            def dummy_reader():
                time.sleep(0.2)
                return None
            return dummy_reader

        def read_key_posix():
            dr, _, _ = select.select([sys.stdin], [], [], 0.05)
            if dr:
                return sys.stdin.read(1).lower()
            return None
        return read_key_posix

def main():
    robot = RobotController(config)
    shutdown_requested = False

    def handle_signal(sig, frame):
        nonlocal shutdown_requested
        if shutdown_requested:
            os._exit(0)
        shutdown_requested = True
        logger.warning(f"Received signal {sig}, initiating clean shutdown...")
        try:
            robot.shutdown()
        finally:
            os._exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    success = robot.start()
    if not success and not config.SIMULATION_MODE:
        logger.error("Initialization failed. Exiting.")
        robot.shutdown()
        sys.exit(1)

    key_reader = get_key_reader()
    is_posix_tty = os.name != "nt" and sys.stdin.isatty()
    old_term_settings = None

    if is_posix_tty:
        import termios
        import tty
        old_term_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

    print("\n--- ROBOT CONTROL CLI & SERVER ---")
    print(f"  Server: http://{config.SERVER_HOST}:{config.SERVER_PORT}")
    print("  [w] Forward")
    print("  [s] Backward")
    print("  [a] Turn Left")
    print("  [d] Turn Right")
    print("  [x] Stop")
    print("  [e] Emergency Stop")
    print("  [r] Reset Emergency Stop")
    print("  [p] Start Pairing Mode (OLED QR)")
    print("  [q] Quit")
    print("-----------------------------------\n")

    try:
        while not shutdown_requested:
            k = key_reader()
            if k is not None and k != "":
                if k == "w":
                    robot.handle_command(MovementCommand.FORWARD)
                elif k == "s":
                    robot.handle_command(MovementCommand.BACKWARD)
                elif k == "a":
                    robot.handle_command(MovementCommand.TURN_LEFT)
                elif k == "d":
                    robot.handle_command(MovementCommand.TURN_RIGHT)
                elif k == "x":
                    robot.handle_command(MovementCommand.STOP)
                elif k == "e":
                    robot.handle_command(MovementCommand.EMERGENCY_STOP)
                elif k == "r":
                    robot.reset_emergency_stop()
                elif k == "p":
                    robot.trigger_pairing_mode()
                elif k == "q":
                    logger.info("User requested exit.")
                    break
            time.sleep(0.05)
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt caught in main loop")
    finally:
        if is_posix_tty and old_term_settings is not None:
            import termios
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_term_settings)
        robot.shutdown()

if __name__ == "__main__":
    main()
