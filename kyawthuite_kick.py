#!/usr/bin/env python3
"""Kyawthuite Kick — molten amber keep-up arcade for ElbowOS. Python 3 + pygame.

Kick a glowing kyawthuite puck into falling crystal shards.
Arrows / A D slide the boot. Space kicks when the puck is close.
"""
import math
import os
import random
import subprocess
import sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get(
    "ELBOWOS_MP4", "/workspace/artifacts/KYAWTHUITE_KICK_ElbowOS.mp4"
)
TITLE, HANDLE = "KYAWTHUITE KICK", "x.com/ElbowOS"
INK = (10, 5, 8)
AMBER = (255, 156, 42)
CREAM = (255, 232, 190)
TEAL = (46, 230, 206)
MAG = (255, 64, 150)
GOLD = (255, 210, 70)
SHARD_COLS = (AMBER, TEAL, MAG, GOLD)


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption(TITLE)
        self.font = pygame.font.SysFont("dejavusans", 64, bold=True)
        self.small = pygame.font.SysFont("dejavusans", 36, bold=True)
        self.tiny = pygame.font.SysFont("dejavusans", 28)
        self.reset()

    def reset(self):
        self.t = 0
        self.score = 0
        self.combo = 0
        self.boot = W / 2
        self.tilt = 0.0
        self.px, self.py = W / 2, 1280
        self.vx, self.vy = 220.0, -640.0
        self.shards = []
        self.sparks = []
        self.embers = [
            [random.randrange(W), random.randrange(H), random.uniform(40, 140)]
            for _ in range(48)
        ]
        self.spawn_cd = 0.2

    def kick(self, power=1.0):
        self.vy = -780 - 220 * power
        self.vx += (self.px - self.boot) * 1.6 + self.tilt * 420
        self.vx = max(-720, min(720, self.vx))
        self.combo = min(self.combo + 1, 9)

    def burst(self, x, y, col, n=10):
        for _ in range(n):
            a = random.random() * math.tau
            s = random.uniform(80, 360)
            self.sparks.append([x, y, math.cos(a) * s, math.sin(a) * s, col, 0.45])

    def update(self, dt, keys, auto):
        self.t += dt
        target = self.px
        if auto:
            if keys:
                pass
            self.boot += (target - self.boot) * min(1, dt * 7.5)
            if self.py > 1500 and self.vy > 0 and abs(self.px - self.boot) < 160:
                self.kick(0.8 + 0.2 * math.sin(self.t * 3))
        else:
            spd = 780
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.boot -= spd * dt
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.boot += spd * dt
        self.boot = max(120, min(W - 120, self.boot))
        self.tilt = max(-0.55, min(0.55, (self.px - self.boot) / 280))
        self.vy += 980 * dt
        self.px += self.vx * dt
        self.py += self.vy * dt
        if self.px < 46 or self.px > W - 46:
            self.px = max(46, min(W - 46, self.px))
            self.vx *= -0.92
        if self.py < 220:
            self.py = 220
            self.vy = abs(self.vy) * 0.7
        if self.py > 1760 and self.vy > 0:
            if abs(self.px - self.boot) < 150:
                self.kick(1.0)
                self.py = 1700
                self.burst(self.px, self.py, CREAM, 6)
            else:
                self.score = max(0, self.score - 5)
                self.combo = 0
                self.px, self.py = self.boot, 1500
                self.vx, self.vy = random.uniform(-180, 180), -520
        self.spawn_cd -= dt
        if self.spawn_cd <= 0:
            self.spawn_cd = random.uniform(0.28, 0.55)
            self.shards.append(
                {
                    "x": random.uniform(90, W - 90),
                    "y": 250,
                    "r": random.randint(28, 48),
                    "vy": random.uniform(160, 320),
                    "vx": random.uniform(-40, 40),
                    "c": random.choice(SHARD_COLS),
                    "spin": random.uniform(-3, 3),
                    "a": random.random() * math.tau,
                }
            )
        alive = []
        for s in self.shards:
            s["y"] += s["vy"] * dt
            s["x"] += s["vx"] * dt
            s["a"] += s["spin"] * dt
            if s["y"] > H + 40:
                continue
            dx, dy = s["x"] - self.px, s["y"] - self.py
            if dx * dx + dy * dy < (s["r"] + 28) ** 2:
                self.score += 10 + self.combo * 2
                self.burst(s["x"], s["y"], s["c"])
                self.vx += dx * 1.4
                self.vy = -abs(self.vy) * 0.55 - 180
                continue
            alive.append(s)
        self.shards = alive[-18:]
        nxt = []
        for sp in self.sparks:
            sp[0] += sp[2] * dt
            sp[1] += sp[3] * dt
            sp[5] -= dt
            if sp[5] > 0:
                nxt.append(sp)
        self.sparks = nxt
        for e in self.embers:
            e[1] -= e[2] * dt
            if e[1] < 180:
                e[1] = H - 40
                e[0] = random.randrange(W)

    def draw(self, surf):
        surf.fill(INK)
        for i in range(18):
            y = 200 + i * 96
            shade = 18 + int(12 * math.sin(self.t * 1.4 + i))
            pygame.draw.rect(surf, (shade + 28, shade, 8), (0, y, W, 90))
        pygame.draw.rect(surf, (48, 18, 6), (40, 180, W - 80, H - 260), 6, border_radius=28)
        for e in self.embers:
            pygame.draw.circle(surf, (180, 70, 20), (int(e[0]), int(e[1])), 3)
        for s in self.shards:
            pts = []
            for k in range(6):
                ang = s["a"] + k * math.tau / 6
                pts.append(
                    (s["x"] + math.cos(ang) * s["r"], s["y"] + math.sin(ang) * s["r"])
                )
            pygame.draw.polygon(surf, s["c"], pts)
            pygame.draw.polygon(surf, CREAM, pts, 3)
        for sp in self.sparks:
            pygame.draw.circle(surf, sp[4], (int(sp[0]), int(sp[1])), 5)
        bx, by = self.boot, 1748
        toe = 130
        poly = [
            (bx - toe, by + 28),
            (bx + toe, by + 18),
            (bx + toe * 0.55 + self.tilt * 40, by - 36),
            (bx - toe * 0.7, by - 22),
        ]
        pygame.draw.polygon(surf, AMBER, poly)
        pygame.draw.polygon(surf, CREAM, poly, 4)
        pygame.draw.circle(surf, (255, 190, 80), (int(self.px), int(self.py)), 36)
        pygame.draw.circle(surf, GOLD, (int(self.px), int(self.py)), 22)
        pygame.draw.circle(surf, CREAM, (int(self.px - 6), int(self.py - 6)), 8)
        banner = pygame.Surface((W, 160), pygame.SRCALPHA)
        banner.fill((8, 4, 6, 210))
        surf.blit(banner, (0, 0))
        title = self.font.render(TITLE, True, AMBER)
        surf.blit(title, title.get_rect(center=(W // 2, 58)))
        score = self.small.render(f"SCORE  {self.score}", True, CREAM)
        surf.blit(score, score.get_rect(center=(W // 2, 122)))
        foot = pygame.Surface((W, 90), pygame.SRCALPHA)
        foot.fill((8, 4, 6, 200))
        surf.blit(foot, (0, H - 90))
        tag = self.small.render(HANDLE, True, TEAL)
        surf.blit(tag, tag.get_rect(center=(W // 2, H - 48)))

    def play_interactive(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            dt = min(clock.tick(FPS) / 1000, 0.05)
            keys = pygame.key.get_pressed()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    if abs(self.px - self.boot) < 180 and self.py > 1400:
                        self.kick()
            self.update(dt, keys, False)
            self.draw(self.screen)
            pygame.display.flip()
        pygame.quit()

    def record(self):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-preset", "veryfast", "-movflags", "+faststart",
            OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        frame = pygame.Surface((W, H))
        dt = 1 / FPS
        try:
            for _ in range(FPS * SECS):
                self.update(dt, None, True)
                self.draw(frame)
                proc.stdin.write(pygame.image.tobytes(frame, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1200:]}")
        print("wrote", OUT)
        pygame.quit()


def main():
    g = Game()
    if PLAY and not RECORD:
        g.play_interactive()
    else:
        g.record()


if __name__ == "__main__":
    main()
