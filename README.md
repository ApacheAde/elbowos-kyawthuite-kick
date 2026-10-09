# Kyawthuite Kick

Full-colour Python 3 molten amber keep-up arcade for ElbowOS.

Slide an amber boot and kick a glowing kyawthuite puck into falling crystal shards. Amber, teal, magenta, and gold hexes score on contact. Missing the puck costs a little score and drops it back onto the boot.

Not a commercial emulator and not a ROM. Original rules and art.

## Play

```bash
pip install -r requirements.txt
python3 kyawthuite_kick.py --play
```

Arrows or A / D slide. Space kicks when the puck is close to the boot.

## Record a 9:16 reel

```bash
python3 kyawthuite_kick.py --record
```

Writes a 15 second 1080x1920 H.264 MP4 (dummy SDL video driver, ffmpeg libx264 yuv420p CRF 20, +faststart).

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/1Z-J59wP1QJ_RVKYP343I2pDp1zLV5fZX/view
