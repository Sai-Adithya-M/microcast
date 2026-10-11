// MicroCast — Clean Outdoor Controller
let selectedCloudCode = 3;
let currentPrediction = null;
let currentAudioElement = null;

const presets = {
  calm: { pressure: 0.2, alt: 1800, temp: 19.5, hum: 45, wind: 12, cloud: 0 },
  wave: { pressure: 1.4, alt: 2300, temp: 13.0, hum: 76, wind: 36, cloud: 2 },
  squall: { pressure: 2.8, alt: 2750, temp: 6.8, hum: 94, wind: 54, cloud: 4 }
};

document.addEventListener("DOMContentLoaded", () => {
  setupSliders();
  setupCloudButtons();
  setupPresetPills();
  setupPhotoUpload();
  setupSampleButtons();
  setupScanButton();
  setupAudioPlayer();

  // Run initial forecast
  triggerForecast();
});

function setupSliders() {
  const pDrop = document.getElementById("pressure-drop");
  const alt = document.getElementById("altitude");
  const temp = document.getElementById("temperature");
  const hum = document.getElementById("humidity");
  const wind = document.getElementById("wind");

  pDrop.addEventListener("input", (e) => {
    document.getElementById("val-pressure").textContent = `${parseFloat(e.target.value).toFixed(1)} hPa/hr`;
  });

  alt.addEventListener("input", (e) => {
    const val = parseInt(e.target.value);
    document.getElementById("val-altitude").textContent = `${val.toLocaleString()} m`;
    document.getElementById("header-elevation").textContent = `${val.toLocaleString()} m`;
  });

  temp.addEventListener("input", (e) => {
    document.getElementById("val-temp").textContent = `${parseFloat(e.target.value).toFixed(1)} °C`;
  });

  hum.addEventListener("input", (e) => {
    document.getElementById("val-humidity").textContent = `${e.target.value}%`;
  });

  wind.addEventListener("input", (e) => {
    document.getElementById("val-wind").textContent = `${e.target.value} km/h`;
  });
}

function setupCloudButtons() {
  const btns = document.querySelectorAll(".cloud-btn");
  btns.forEach(btn => {
    btn.addEventListener("click", () => {
      btns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      selectedCloudCode = parseInt(btn.dataset.code);
    });
  });
}

function selectCloudCode(code) {
  selectedCloudCode = code;
  document.querySelectorAll(".cloud-btn").forEach(btn => {
    btn.classList.toggle("active", parseInt(btn.dataset.code) === code);
  });
}

function setupPresetPills() {
  const pills = document.querySelectorAll(".preset-pill");
  pills.forEach(pill => {
    pill.addEventListener("click", () => {
      pills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");

      const p = presets[pill.dataset.preset];
      if (p) {
        document.getElementById("pressure-drop").value = p.pressure;
        document.getElementById("val-pressure").textContent = `${p.pressure.toFixed(1)} hPa/hr`;

        document.getElementById("altitude").value = p.alt;
        document.getElementById("val-altitude").textContent = `${p.alt.toLocaleString()} m`;
        document.getElementById("header-elevation").textContent = `${p.alt.toLocaleString()} m`;

        document.getElementById("temperature").value = p.temp;
        document.getElementById("val-temp").textContent = `${p.temp.toFixed(1)} °C`;

        document.getElementById("humidity").value = p.hum;
        document.getElementById("val-humidity").textContent = `${p.hum}%`;

        document.getElementById("wind").value = p.wind;
        document.getElementById("val-wind").textContent = `${p.wind} km/h`;

        selectCloudCode(p.cloud);
        triggerForecast();
      }
    });
  });
}

function setupPhotoUpload() {
  const fileInput = document.getElementById("camera-input");
  const dropZone = document.getElementById("drop-zone");
  const removeBtn = document.getElementById("remove-photo-btn");

  dropZone.addEventListener("click", (e) => {
    if (e.target !== removeBtn) {
      fileInput.click();
    }
  });

  removeBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    resetPhotoUpload();
  });

  fileInput.addEventListener("change", async (e) => {
    if (e.target.files && e.target.files[0]) {
      await processImageFile(e.target.files[0]);
    }
  });

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.style.borderColor = "var(--color-primary)";
  });
  dropZone.addEventListener("dragleave", () => {
    dropZone.style.borderColor = "var(--border-light)";
  });
  dropZone.addEventListener("drop", async (e) => {
    e.preventDefault();
    dropZone.style.borderColor = "var(--border-light)";
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await processImageFile(e.dataTransfer.files[0]);
    }
  });
}

function resetPhotoUpload() {
  document.getElementById("camera-input").value = "";
  document.getElementById("preview-box").classList.add("hidden");
  document.getElementById("upload-placeholder").classList.remove("hidden");
  document.getElementById("vision-badge").classList.add("hidden");
}

async function processImageFile(file) {
  const preview = document.getElementById("image-preview");
  const previewBox = document.getElementById("preview-box");
  const placeholder = document.getElementById("upload-placeholder");

  preview.src = URL.createObjectURL(file);
  previewBox.classList.remove("hidden");
  placeholder.classList.add("hidden");

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/analyze-sky", {
      method: "POST",
      body: formData
    });
    const vision = await res.json();

    // Show clean vision badge
    const badge = document.getElementById("vision-badge");
    const title = document.getElementById("vision-title");
    const sub = document.getElementById("vision-subtitle");

    title.textContent = `${vision.cloud_name} (${vision.confidence_percent}% match)`;
    sub.textContent = `${vision.description} Synced with trail model.`;
    badge.classList.remove("hidden");

    // Update active cloud selection
    selectCloudCode(vision.cloud_type_code);

    // Auto-trigger forecast
    triggerForecast();
  } catch (err) {
    console.error("Photo analysis failed:", err);
  }
}

function setupSampleButtons() {
  const btns = document.querySelectorAll(".btn-sample");
  btns.forEach(btn => {
    btn.addEventListener("click", () => {
      const type = btn.dataset.sample;
      createSamplePhoto(type);
    });
  });
}

function createSamplePhoto(type) {
  const canvas = document.createElement("canvas");
  canvas.width = 400;
  canvas.height = 220;
  const ctx = canvas.getContext("2d");

  if (type === "clear") {
    // Pure blue sky
    const g = ctx.createLinearGradient(0, 0, 0, 220);
    g.addColorStop(0, "#2563eb");
    g.addColorStop(0.6, "#60a5fa");
    g.addColorStop(1, "#bfdbfe");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 400, 220);
  } else if (type === "wave") {
    // Wave cloud
    const g = ctx.createLinearGradient(0, 0, 0, 220);
    g.addColorStop(0, "#3b82f6");
    g.addColorStop(1, "#94a3b8");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 400, 220);

    ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
    ctx.beginPath();
    ctx.ellipse(200, 100, 150, 40, 0, 0, Math.PI * 2);
    ctx.fill();
  } else if (type === "anvil") {
    // Storm anvil
    const g = ctx.createLinearGradient(0, 0, 0, 220);
    g.addColorStop(0, "#f1f5f9");
    g.addColorStop(0.3, "#94a3b8");
    g.addColorStop(0.7, "#334155");
    g.addColorStop(1, "#0f172a");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 400, 220);

    ctx.fillStyle = "#1e293b";
    ctx.fillRect(0, 150, 400, 70);
  }

  canvas.toBlob((blob) => {
    const file = new File([blob], `sample_${type}.jpg`, { type: "image/jpeg" });
    processImageFile(file);
  }, "image/jpeg");
}

function setupScanButton() {
  document.getElementById("scan-btn").addEventListener("click", () => {
    triggerForecast();
  });
}

async function triggerForecast() {
  const btn = document.getElementById("scan-btn");
  btn.style.opacity = "0.7";
  btn.textContent = "Running TabPFN inference...";

  const payload = {
    pressure_drop_hpa_hr: parseFloat(document.getElementById("pressure-drop").value),
    altitude_m: parseFloat(document.getElementById("altitude").value),
    temp_c: parseFloat(document.getElementById("temperature").value),
    humidity_pct: parseFloat(document.getElementById("humidity").value),
    wind_speed_kmh: parseFloat(document.getElementById("wind").value),
    cloud_type_code: selectedCloudCode
  };

  try {
    const res = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    currentPrediction = data;
    renderResults(data);
  } catch (err) {
    console.error("Forecast error:", err);
  } finally {
    btn.style.opacity = "1";
    btn.textContent = "Run Forecast Scan";
  }
}

function renderResults(data) {
  const percent = data.risk_percent;
  document.getElementById("risk-display-number").textContent = `${percent}%`;

  // Risk bar
  const fill = document.getElementById("risk-bar-fill");
  fill.style.width = `${Math.max(percent, 4)}%`;
  fill.className = "risk-bar-fill";

  // Severity Pill
  const pill = document.getElementById("severity-pill");
  pill.className = "pill-severity";

  if (percent >= 75) {
    fill.classList.add("danger");
    pill.classList.add("danger");
    pill.textContent = "Storm Warning";
  } else if (percent >= 45) {
    fill.classList.add("watch");
    pill.classList.add("watch");
    pill.textContent = "Storm Watch";
  } else {
    fill.classList.add("safe");
    pill.classList.add("safe");
    pill.textContent = "Safe / Stable";
  }

  document.getElementById("eta-time").textContent = data.estimated_window;
  document.getElementById("advice-text").textContent = data.action;
}

function setupAudioPlayer() {
  const btn = document.getElementById("play-audio-btn");
  btn.addEventListener("click", () => {
    playAudioAlert();
  });
}

function playAudioAlert() {
  if (!currentPrediction) return;

  const label = document.getElementById("audio-label");

  // If backend provided an MP3 (ElevenLabs)
  if (currentPrediction.narration && currentPrediction.narration.audio_url) {
    if (currentAudioElement) currentAudioElement.pause();
    currentAudioElement = new Audio(currentPrediction.narration.audio_url);
    label.textContent = "Playing...";
    currentAudioElement.play();
    currentAudioElement.onended = () => { label.textContent = "Listen to Alert"; };
    return;
  }

  // Native browser speech synthesis
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
    const text = currentPrediction.narration ? currentPrediction.narration.speech_text : currentPrediction.action;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    label.textContent = "Playing...";
    utterance.onend = () => { label.textContent = "Listen to Alert"; };
    window.speechSynthesis.speak(utterance);
  }
}
