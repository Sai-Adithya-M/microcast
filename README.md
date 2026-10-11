# ⛰️ MicroCast — Offline Mountain Squall & Sky-Reader

> **Hacktoberfest Open-Source AI Challenge: Week 1 — "Touch Grass"**  
> An offline, zero-shot mountain squall and microclimate predictor powered by **Prior Labs' TabPFN**. Built for screen-free backcountry trail safety.

---

## 🧭 The Core Concept: "Touch Grass" with Zero Screen Time

When hiking in high-altitude terrain, deep valleys, or national parks, there is **zero cell reception**. Cloud APIs, radar apps, and commercial weather feeds are completely dead. Mountain weather can turn from calm alpine sunshine into a lethal freezing squall within 45 minutes.

Traditional mountaineers read physical indicators:
1. **Barometric pressure trends** (a drop > 1.5 hPa/hour signals an incoming front).
2. **Cloud morphology** (altocumulus lenticularis or towering congestus precursors).

**MicroCast** brings open-source tabular AI to the backcountry:
- It takes local sensor telemetry and uses **Prior Labs' TabPFN** foundation model to forecast microclimate storm risk with **zero fine-tuning**.
- Once calculated, it converts the safety directive into an **audio whisper** directly in your trail earbuds.
- **Screen time:** **2 seconds**. You check your instrument, slip the phone back into your pack, and navigate the trail with your hands free.

---

## ⚡ Partner Prize Categories Entered

1. **#best-use-of-tabpfn ($200 Prize):**  
   Uses **Prior Labs' TabPFN** in-context tabular foundation model to perform zero-shot classification on mountain atmospheric telemetry (pressure drop rates, elevation, ambient temperature, relative humidity, ridge wind speeds). No training, no gradient updates—runs in milliseconds directly on CPU.

2. **#best-use-of-render ($200 Prize):**  
   Deployed as an asynchronous FastAPI microservice on **Render**, serving real-time predictions and offline field instrumentation.

3. **ElevenLabs / Audio Guide ($100 Prize):**  
   Dynamic hands-free trail narrator producing natural, calm audio advisories so hikers never look at screens while navigating technical mountain trails.

---

## 🚀 Quickstart: Running Locally

### 1. Prerequisites
- Python 3.9+

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/your-username/microcast.git
cd microcast

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run MicroCast
```bash
python3 server.py
```
Open **`http://localhost:8000`** in your browser.

---

## 📁 Project Structure

```
├── core/
│   ├── predictor.py         # TabPFN zero-shot tabular inference engine
│   └── audio_narrator.py    # Hands-free trail voice narrator
├── data/
│   └── mountain_weather_history.csv  # Historical alpine telemetry dataset
├── static/
│   ├── index.html           # Dark-mode tactical field HUD
│   ├── style.css            # High-contrast outdoor instrument styling
│   └── app.js               # Client controller with Web Speech & ElevenLabs
├── server.py                # FastAPI backend service
└── requirements.txt         # Clean dependency manifest
```

---

## 📝 Why Open Innovation Matters (Dev.to Essay Excerpt)

> Proprietary cloud AI requires gigabit connections and multi-gigabyte server farms. But real life happens outdoors—on rocky ridges, across misty trailheads, and deep in national parks where cell towers don't exist.
> 
> Open-weight innovation matters because **resilience in the physical world requires local computing**. With open foundation models like TabPFN running directly on edge devices without requiring cloud handshakes, outdoor enthusiasts gain reliable decision support that doesn't cost subscription tokens and never fails when the cell bars drop to zero.
