import argparse
import math
import random
import time


class VirtualFramebuffer:
    def __init__(self, width: int = 48, height: int = 12):
        self.width = width
        self.height = height
        self.buffer = [[" " for _ in range(width)] for _ in range(height)]

    def clear(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                self.buffer[y][x] = " "

    def write_text(self, x: int, y: int, text: str) -> None:
        if y < 0 or y >= self.height:
            return
        for i, ch in enumerate(text):
            xx = x + i
            if 0 <= xx < self.width:
                self.buffer[y][xx] = ch

    def draw_bar(self, x: int, y: int, width: int, fraction: float) -> None:
        clamped = max(0.0, min(1.0, fraction))
        filled = int(width * clamped)
        for i in range(width):
            ch = "#" if i < filled else "."
            xx = x + i
            if 0 <= y < self.height and 0 <= xx < self.width:
                self.buffer[y][xx] = ch

    def render(self) -> str:
        border = "+" + "-" * self.width + "+"
        lines = [border]
        for row in self.buffer:
            lines.append("|" + "".join(row) + "|")
        lines.append(border)
        return "\n".join(lines)


def fake_sensor_sample(tick: int) -> dict:
    baseline = 42.0
    wave = math.sin(tick / 8.0) * 6.0
    noise = random.uniform(-0.6, 0.6)
    temp_c = baseline + wave + noise
    vibration_g = 0.3 + abs(math.sin(tick / 4.0)) * 1.1 + random.uniform(-0.05, 0.05)
    return {"temp_c": temp_c, "vibration_g": vibration_g}


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal VDK demo (framebuffer + fake sensor + loop)")
    parser.add_argument("--steps", type=int, default=120, help="number of loop steps to run")
    parser.add_argument("--fps", type=float, default=12.0, help="refresh rate")
    args = parser.parse_args()

    fb = VirtualFramebuffer()
    frame_time = 1.0 / max(args.fps, 1.0)

    for tick in range(args.steps):
        sample = fake_sensor_sample(tick)
        temp_c = sample["temp_c"]
        vibration_g = sample["vibration_g"]
        alert = temp_c >= 65.0 or vibration_g >= 1.2

        fb.clear()
        fb.write_text(1, 1, "VDK MINIMAL SENSOR MONITOR")
        fb.write_text(1, 3, f"tick: {tick:04d}")
        fb.write_text(1, 4, f"temp_c: {temp_c:05.2f}")
        fb.write_text(1, 5, f"vibration_g: {vibration_g:04.2f}")
        fb.write_text(1, 6, f"alert: {'ON ' if alert else 'off'}")

        # Two virtual LCD bars for quick visual state.
        fb.write_text(1, 8, "TEMP")
        fb.draw_bar(8, 8, 24, (temp_c - 20.0) / 60.0)
        fb.write_text(1, 9, "VIBE")
        fb.draw_bar(8, 9, 24, vibration_g / 2.0)

        # ANSI clear + home keeps output as a single live host window in terminal.
        print("\x1b[2J\x1b[H" + fb.render())
        time.sleep(frame_time)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
