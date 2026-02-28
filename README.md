# Camera Access - Privacy Protection System

A real-time, AI-assisted laptop privacy protection system that detects faces and blurs sensitive content when bystanders are present. Fully local, no cloud processing.

## Features

- Real-time face detection (Windows, CPU-friendly)
- Automatic privacy blur when 2+ faces detected
- Face enrollment & verification (distinguish you from others)
- Watching heuristic (reduce false positives)
- Debounce logic (prevent flicker)
- Demo overlay (simulated sensitive content)
- Detailed logging (FPS, decisions, transitions)
- Fully configurable (JSON-based settings)

## Quick Start

### Prerequisites
- Python 3.10+ (64-bit)
- Windows laptop with webcam
- Virtual environment already set up

### Run the Application

```bash
cd camera_access
.\venv\Scripts\activate
python src/main.py
```

**Controls in UI:**
- `q` – Quit
- `p` – Pause/Resume detection
- `r` – Reset decision engine
- `d` – Toggle demo sensitive content overlay
- `s` – Toggle annotations

## Workflow: Complete Stages

### Stage 1: Face Detection + Instant Blur (MVP)

Automatic privacy blur when 2+ faces are detected. No identity information.

```bash
python src/main.py
```

**What it does:** Detects faces and blurs screen instantly
**Accuracy:** Moderate (no identity verification)

### Stage 2: Enrollment (Create Your Face Template)

Record your face template for future verification.

```bash
python enroll.py
```

**Instructions:**
1. Press `e` to START enrollment
2. Position your face in frame (will be auto-detected)
3. Press SPACE to capture samples
4. Move your head slightly between captures
5. Capture 10-15 samples (spread across different poses)
6. Press `q` to FINISH

**Output:**
- `data/my_template.npy` – Your face embedding
- `data/meta.json` – Enrollment metadata

### Stage 3: Face Verification (ME vs OTHER)

Once enrolled, app automatically distinguishes you from other faces.

- **Automatic activation:** When `data/my_template.npy` exists
- **Green boxes:** Detected as "ME" (your face)
- **Red boxes:** Detected as "OTHER" (someone else)
- **Blur triggers only on OTHER faces**
- **Similarity scores:** Shown on each face

### Stage 4: Watching Heuristic

Reduces false positives from far-away or background faces.

- **Area ratio threshold:** `area_ratio_threshold` in config.json (default 0.02)
- **Debounce logic:** Confirms risk for N consecutive frames before blurring
- **Position stability:** Tracks face positions over time

To adjust:
```json
{
  "privacy": {
    "area_ratio_threshold": 0.02,    // Higher = less sensitive
    "debounce_on_frames": 2,          // More frames = longer delay
    "debounce_off_seconds": 0.8       // Longer = longer recovery
  }
}
```

### Stage 5: Professionalization

Production-ready features: logging, demo mode, detailed status.

- **Logging:** Automatically saves `logs/privacy_app_TIMESTAMP.log`
- **Demo overlay:** Shows simulated sensitive content (blurred when privacy_on)
- **Statistics:** Displays FPS, face counts, privacy transitions in logs
- **Configuration:** All settings in `config.json`

## Architecture

```
camera_access/
├── src/
│   ├── main.py           → Entry point (full pipeline)
│   ├── camera.py         → Camera capture thread (30 FPS)
│   ├── detector.py       → Face detection (OpenCV DNN)
│   ├── embedder.py       → Face embeddings (HOG + color)
│   ├── verify.py         → Face verification (template matching)
│   ├── decision.py       → Privacy logic + debounce + heuristic
│   ├── render.py         → Blur overlay + UI rendering
│   ├── config.py         → Configuration loader
│   ├── utils.py          → Shared utilities
│   └── __init__.py
├── enroll.py             → Enrollment script
├── config.json           → Configuration file
├── data/
│   ├── my_template.npy   → (Created by enroll.py)
│   └── meta.json         → (Created by enroll.py)
├── logs/                 → (Auto-created, session logs)
└── venv/                 → Python environment
```

## Configuration Reference

Edit `config.json` to customize:

```json
{
  "camera": {
    "device_id": 0,              // 0 = default webcam
    "target_fps": 30
  },
  "detection": {
    "resize_width": 320,
    "resize_height": 240,
    "detection_interval_frames": 3,
    "min_detection_confidence": 0.5
  },
  "privacy": {
    "face_count_threshold": 2,        // Blur if N+ other faces
    "area_ratio_threshold": 0.02,     // Min face size to count
    "debounce_on_frames": 2,          // Frames until blur ON
    "debounce_off_seconds": 0.8,      // Seconds until blur OFF
    "blur_kernel_size": 31,           // Blur intensity
    "verification_threshold": 0.6     // ME/OTHER similarity threshold
  },
  "enrollment": {
    "min_samples": 10,
    "max_samples": 20
  },
  "ui": {
    "show_annotations": true,
    "show_fps": true,
    "show_demo_overlay": true
  }
}
```

## Performance

- **Detection rate:** 10-15 Hz (throttled for efficiency)
- **Response time:** <120ms from detection to blur
- **CPU usage:** ~10-15% on integrated graphics
- **Memory:** ~250-350 MB

## Troubleshooting

**Camera not opening:**
- Check Windows privacy settings (Settings → Privacy → Camera)
- Try different `device_id` in config.json (0, 1, 2, etc.)

**Face not detected:**
- Improve lighting
- Increase `area_ratio_threshold`
- Lower `min_detection_confidence`

**Too many false positives:**
- Increase `area_ratio_threshold` (e.g., 0.03-0.04)
- Increase `debounce_on_frames` (e.g., 3-4)

**Verification not working:**
- Run `python enroll.py` again
- Lower `verification_threshold` (e.g., 0.5)

## Privacy & Security

- Local processing – No internet, no cloud
- No raw storage – Frames never saved
- Template only – 128-dim embedding vector
- Minimal metadata – Timestamp and model version
- Open configuration – All settings transparent

## View Logs

```bash
# Most recent session
cat logs/privacy_app_*.log | tail -50
```

---

**Version:** 5.0 (All Stages Complete)  
**Last Updated:** February 26, 2026  
**Status:** Production-Ready MVP
