# Camera Access Privacy Protection System
## Quick Start & Demo Guide

**Status:** ✅ PRODUCTION-READY  
**All 5 Stages:** Implemented & Tested  
**Last Updated:** February 26, 2026

---

## 🚀 Quick Launch

### Option A: Run Batch Script (Easiest)
```bash
double-click run.bat
```

### Option B: Manual Launch
```bash
cd camera_access
.\venv\Scripts\activate
python src/main.py
```

---

## 📋 Full Demo Workflow

### 1️⃣ First Run: Stage 1 (Face Detection + Blur)

**What to do:**
1. Run the application: `python src/main.py`
2. Face the camera
3. Have a second person enter the frame
4. **Expected:** Screen blurs automatically when 2+ faces detected

**Controls while running:**
- `q` = Quit
- `p` = Pause/Resume detection
- `d` = Show/hide demo overlay (simulated sensitive content)
- `s` = Show/hide face annotations

**What you'll see:**
- Privacy status (green = OFF, red = ON)
- Face bounding boxes with confidence scores
- Real-time FPS counter
- Red tint when privacy mode active

---

### 2️⃣ Enrollment: Stage 2 (Create Your Face Template)

**When:** After Stage 1 demo (optional, enables better verification)

**What to do:**
```bash
double-click enroll.bat
# OR manually: python enroll.py
```

**Enrollment Process:**
1. Face the camera
2. Press `e` to START enrollment
3. Press `SPACE` to capture face samples
4. Move your head slightly between captures
5. Capture 10-15 samples (from different angles)
6. Press `q` to FINISH

**Expected Output:**
- `data/my_template.npy` created
- `data/meta.json` created
- Console prints: "SUCCESS! Enrollment complete!"

---

### 3️⃣ Enhanced Mode: Stage 3 (Verification ON)

**What happens:**
1. Run app again: `python src/main.py`
2. App auto-detects template from Step 2
3. **New:** Face verification is ENABLED
4. **New:** Your face labeled "ME" (green box)
5. **New:** Other faces labeled "OTHER" (red box)
6. **New:** Blur triggers ONLY when OTHER faces present

**UI Changes:**
- Green labels with YOUR similarity score
- Red labels with OTHER similarity scores
- Status shows "ME" and "OTHER" counts

**Test:**
- Solo: You alone → NO blur
- With someone: You + other person → blur ON
- Their face prominent: Blur stays ON
- They exit frame: Blur OFF (after 0.8s cooldown)

---

### 4️⃣ Smart Mode: Stage 4 (Watching Heuristic)

**Already Active:** Automatically running with Stage 3

**What it does:**
- Only counts faces close enough to "watch" your screen
- Far-away faces (background, etc.) ignored
- Smooth transitions with debounce logic

**Test:**
- Have someone stand far away: NO blur (face too small)
- Have them move close: Blur triggers (face larger)
- Stand between: Blur depends on area ratio

**Tuning (if needed):**
Edit `config.json`:
```json
{
  "privacy": {
    "area_ratio_threshold": 0.02   // Increase to make less sensitive
  }
}
```

---

### 5️⃣ Professional Features: Stage 5 (Logging & Demo)

**Auto-enabled:**
- Logs saved to: `logs/privacy_app_TIMESTAMP.log`
- Demo overlay shows simulated sensitive content
- Toggle with `d` key

**View Logs:**
```bash
# Show most recent log
type logs\privacy_app_*.log | tail -50

# Or open in editor
notepad logs\privacy_app_*.log
```

**Log Output Example:**
```
2026-02-26 10:15:32 [INFO] ========== CAMERA ACCESS PRIVACY PROTECTION SYSTEM ==========
2026-02-26 10:15:32 [INFO] [OK] Template found - Face verification ENABLED
2026-02-26 10:15:35 [INFO] Camera started (device=0, fps=30)
2026-02-26 10:15:40 [INFO] [15] Privacy turned ON: Risk: 1 OTHER face(s) detected
2026-02-26 10:15:43 [INFO] [22] Privacy turned OFF: Safe: 1 ME, 0 OTHER
...
2026-02-26 10:20:45 [INFO] ========== SESSION STATISTICS ==========
2026-02-26 10:20:45 [INFO] Total frames processed: 12500
2026-02-26 10:20:45 [INFO] Total detections: 847
2026-02-26 10:20:45 [INFO] Privacy transitions: 23
```

---

## 🎯 Demo Scenario (10 minutes)

**Setup:** 2 people, 1 laptop with camera

**Minute 1-2:** Stage 1
- Solo: App runs, no blur
- Person 2 enters: Blur activates
- Person 2 exits: Blur deactivates

**Minute 3:** Stage 2 (Optional)
- Person 1 runs `enroll.bat`
- Captures 12 face samples
- Waits for "SUCCESS!" message

**Minute 4-7:** Stage 3
- Restart app
- **New:** Green "ME" label on Person 1
- **New:** Red "OTHER" label on Person 2
- Only Person 2 triggers blur
- Person 1 can stand anywhere (no blur)

**Minute 8:** Stage 4
- Person 2 stands far away: No blur
- Person 2 moves close: Blur triggers
- Shows area-based triggering

**Minute 9:** Stage 5
- Press `d` to show demo overlay
- Sensitive content visible when NO blur
- Sensitive content HIDDEN when blur active
- Press `d` to hide overlay

**Minute 10:** Finish
- Press `q` to quit
- Show console output or logs
- Display "SUCCESS! Application closed"

---

## 🔧 Configuration

### Main Settings (config.json)

```json
{
  "camera": {
    "device_id": 0,         // Webcam number (0=default)
    "target_fps": 30        // Frame rate target
  },
  "detection": {
    "resize_width": 320,    // Lower=faster, Higher=accurate
    "detection_interval_frames": 3  // Every 3 frames
  },
  "privacy": {
    "face_count_threshold": 2,      // Blur at 2+ OTHER faces
    "area_ratio_threshold": 0.02,   // Only count if > 2% of frame
    "debounce_on_frames": 2,        // 2 frames to confirm risk
    "debounce_off_seconds": 0.8,    // 0.8 sec to confirm safe
    "blur_kernel_size": 31,         // Blur strength
    "verification_threshold": 0.6   // ME/OTHER similarity cutoff
  }
}
```

### Quick Tune Patterns

**More sensitive (blur easier):**
```json
{
  "area_ratio_threshold": 0.01,
  "debounce_on_frames": 1,
  "blur_kernel_size": 51
}
```

**Less sensitive (fewer false positives):**
```json
{
  "area_ratio_threshold": 0.04,
  "debounce_on_frames": 3,
  "debounce_off_seconds": 2.0
}
```

---

## 📊 Performance Expectations

| Metric | Value |
|--------|-------|
| **Frame Rate** | 28-30 FPS |
| **Detection Rate** | 10-15 Hz |
| **Response Time** | ~80-100ms |
| **CPU Usage** | 10-15% |
| **Memory** | 250-350 MB |

---

## ❓ Troubleshooting

### "Camera not opening"
**Fix:**
1. Check Windows privacy: Settings → Privacy & Security → Camera
2. Allow Python camera access
3. Try `device_id: 1` in config.json
4. Restart app

### "Face not detected"
**Fix:**
1. Ensure good lighting
2. Face camera squarely
3. Lower `min_detection_confidence` (e.g., 0.4)
4. Increase `area_ratio_threshold` (e.g., 0.01)

### "Verification showing SIMILARITY 0.00"
**Fix:**
1. Run `python enroll.py` again
2. Lower `verification_threshold` (e.g., 0.5)
3. Ensure same lighting conditions

### "Blur doesn't turn off"
**Fix:**
1. Increase `debounce_off_seconds` (e.g., 2.0)
2. Exit all faces completely
3. Press `r` to reset engine

---

## 📁 File Structure

```
camera_access/
├── run.bat                    # ⭐ Double-click to start app
├── enroll.bat                 # ⭐ Double-click to enroll face
├── src/
│   ├── main.py               # Main application
│   ├── camera.py             # Camera capture
│   ├── detector.py           # Face detection
│   ├── embedder.py           # Face embeddings
│   ├── verify.py             # Face verification
│   ├── decision.py           # Privacy logic
│   ├── render.py             # Blur + UI
│   └── utils.py              # Helpers
├── config.json               # ⭐ Settings (edit here)
├── data/
│   ├── my_template.npy       # (Created by enroll.py)
│   └── meta.json             # (Created by enroll.py)
├── logs/
│   └── privacy_app_*.log     # Session logs
└── README.md                 # Full documentation
```

---

## 🎓 What You'll Learn

- Real-time computer vision with OpenCV
- Face detection algorithms (DNN-based)
- Face embeddings and similarity matching
- Multi-threaded I/O (camera + processing)
- UI rendering with privacy overlays
- Debounce and heuristic logic
- Configuration management
- Logging and profiling

---

## 📝 Key Takeaways

✅ **Works locally** – No cloud, no data sent  
✅ **Fast response** – <120ms from detection to blur  
✅ **Smart logic** – Distinguishes user from bystanders  
✅ **Configurable** – All settings in JSON  
✅ **Professional** – Logging, stats, comprehensive UI  

---

**Need Help?** Check README.md or STAGES.md for detailed documentation.

**Ready to go!** 🚀

