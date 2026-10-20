/**
 * Smart Waste Sorting Assistant — Frontend Application
 * Interacts with MobileNetV3 Classifier, OpenStreetMap Leaflet GIS, and Gamification API
 */

let mapInstance = null;
let userMarker = null;
let recyclerMarkers = [];
let routePolyline = null;

let currentCoords = { lat: 12.9716, lon: 77.5946, label: "Bengaluru (Default)" };
let activeStream = null;
let currentClassification = null;
let firstPhotoForFusion = null;

// Audio Chime (Synthesized via Web Audio API, no external audio files required!)
function playSuccessChime() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(523.25, ctx.currentTime); // C5
    osc.frequency.exponentialRampToValueAtTime(659.25, ctx.currentTime + 0.1); // E5
    osc.frequency.exponentialRampToValueAtTime(783.99, ctx.currentTime + 0.2); // G5
    gain.gain.setValueAtTime(0.15, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.35);
  } catch (e) {
    console.log("Audio not allowed yet");
  }
}

// ---------------- Initialize Application ----------------
document.addEventListener("DOMContentLoaded", () => {
  initMap();
  setupEventListeners();
  loadUserProfile();
  loadLeaderboard();
  detectBrowserGeolocation();

  // Check URL query parameters for demo links or automated screenshot captures
  const urlParams = new URLSearchParams(window.location.search);
  const targetTab = urlParams.get("tab");
  if (targetTab) {
    const tabBtn = document.querySelector(`[data-tab="tab-${targetTab}"]`);
    if (tabBtn) tabBtn.click();
  }

  const autoSample = urlParams.get("auto_test");
  if (autoSample) {
    const sampleMap = {
      plastic: "plastic_bottle.jpg",
      paper: "cardboard_box.jpg",
      metal: "aluminum_can.jpg",
      glass: "glass_bottle.jpg",
      organic: "organic_food.jpg",
      ewaste: "electronic_device.jpg",
    };
    const imgName = sampleMap[autoSample.toLowerCase()] || "plastic_bottle.jpg";
    setTimeout(() => {
      window.testSample(autoSample, imgName);
    }, 300);
  }
});

// ---------------- Map Initialization (Leaflet) ----------------
function initMap() {
  const mapContainer = document.getElementById("recycling-map");
  if (!mapContainer) return;

  mapInstance = L.map("recycling-map").setView([currentCoords.lat, currentCoords.lon], 13);

  // Standard Public OpenStreetMap tiles (100% Free, no watermark, no key)
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
  }).addTo(mapInstance);

  updateUserMapLocation(currentCoords.lat, currentCoords.lon);
}

function updateUserMapLocation(lat, lon) {
  currentCoords.lat = lat;
  currentCoords.lon = lon;

  if (!mapInstance) return;

  if (userMarker) {
    mapInstance.removeLayer(userMarker);
  }

  const userIcon = L.divIcon({
    className: "custom-user-pin",
    html: `<div style="background: #10B981; width: 18px; height: 18px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 10px #10b981;"></div>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  });

  userMarker = L.marker([lat, lon], { icon: userIcon })
    .addTo(mapInstance)
    .bindPopup(`<b>Your Current Location</b><br>GPS: ${lat.toFixed(4)}, ${lon.toFixed(4)}`);

  mapInstance.setView([lat, lon], 13);
  fetchNearbyRecyclers(null);
}

// ---------------- Event Listeners ----------------
function setupEventListeners() {
  // Navigation Tabs
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach((b) => {
        b.classList.remove("border-emerald-500", "text-emerald-400");
        b.classList.add("border-transparent", "text-gray-400");
      });
      btn.classList.add("border-emerald-500", "text-emerald-400");
      btn.classList.remove("border-transparent", "text-gray-400");

      const target = btn.getAttribute("data-tab");
      document.querySelectorAll(".tab-content").forEach((c) => c.classList.add("hidden"));
      const activeContent = document.getElementById(target);
      if (activeContent) activeContent.classList.remove("hidden");

      if (target === "tab-map" && mapInstance) {
        setTimeout(() => mapInstance.invalidateSize(), 200);
      }
    });
  });

  // Camera Buttons
  const startCameraBtn = document.getElementById("start-camera-btn");
  const captureCameraBtn = document.getElementById("capture-camera-btn");
  const stopCameraBtn = document.getElementById("stop-camera-btn");

  if (startCameraBtn) startCameraBtn.addEventListener("click", startWebcam);
  if (captureCameraBtn) captureCameraBtn.addEventListener("click", captureWebcamFrame);
  if (stopCameraBtn) stopCameraBtn.addEventListener("click", stopWebcam);

  // File Upload
  const fileInput = document.getElementById("waste-file-input");
  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files[0]) {
        uploadFileForClassification(e.target.files[0]);
      }
    });
  }

  // Location Preset Selector
  const citySelect = document.getElementById("city-preset-select");
  if (citySelect) {
    citySelect.addEventListener("change", (e) => {
      const val = e.target.value;
      if (val === "current") {
        detectBrowserGeolocation();
      } else {
        const [lat, lon] = val.split(",").map(Number);
        updateUserMapLocation(lat, lon);
      }
    });
  }

  // Filter recyclers by type
  const filterSelect = document.getElementById("waste-filter-select");
  if (filterSelect) {
    filterSelect.addEventListener("change", (e) => {
      fetchNearbyRecyclers(e.target.value || null);
    });
  }

  // Confirm Action & Earn Points Button
  const confirmActionBtn = document.getElementById("confirm-sorted-btn");
  if (confirmActionBtn) {
    confirmActionBtn.addEventListener("click", handleSortConfirmation);
  }
}

// ---------------- Geolocation ----------------
function detectBrowserGeolocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        updateUserMapLocation(pos.coords.latitude, pos.coords.longitude);
      },
      (err) => {
        console.log("Geolocation permission denied or timeout, using default location.");
      },
      { timeout: 5000 }
    );
  }
}

// ---------------- Webcam Management ----------------
async function startWebcam() {
  const videoElem = document.getElementById("webcam-video");
  const scannerContainer = document.getElementById("camera-container");
  const scanOverlay = document.getElementById("scanner-overlay");

  try {
    activeStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment", width: { ideal: 640 }, height: { ideal: 640 } },
    });
    videoElem.srcObject = activeStream;
    videoElem.play();
    scannerContainer.classList.remove("hidden");
    if (scanOverlay) scanOverlay.classList.remove("hidden");

    document.getElementById("start-camera-btn").classList.add("hidden");
    document.getElementById("capture-camera-btn").classList.remove("hidden");
    document.getElementById("stop-camera-btn").classList.remove("hidden");
  } catch (err) {
    alert("Camera access was not granted or not supported on this device. Please use file upload or sample gallery!");
  }
}

function stopWebcam() {
  if (activeStream) {
    activeStream.getTracks().forEach((t) => t.stop());
    activeStream = null;
  }
  const videoElem = document.getElementById("webcam-video");
  if (videoElem) videoElem.srcObject = null;

  document.getElementById("camera-container").classList.add("hidden");
  document.getElementById("start-camera-btn").classList.remove("hidden");
  document.getElementById("capture-camera-btn").classList.add("hidden");
  document.getElementById("stop-camera-btn").classList.add("hidden");
}

function captureWebcamFrame() {
  const videoElem = document.getElementById("webcam-video");
  if (!videoElem) return;

  const canvas = document.createElement("canvas");
  canvas.width = videoElem.videoWidth || 480;
  canvas.height = videoElem.videoHeight || 480;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(videoElem, 0, 0, canvas.width, canvas.height);

  const base64Data = canvas.toDataURL("image/jpeg", 0.9);
  displayPreview(base64Data);
  classifyBase64(base64Data);
}

// ---------------- Classification Handlers ----------------
async function uploadFileForClassification(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    displayPreview(e.target.result);
  };
  reader.readAsDataURL(file);

  const formData = new FormData();
  formData.append("file", file);
  if (currentCoords.lat && currentCoords.lon) {
    formData.append("lat", currentCoords.lat);
    formData.append("lon", currentCoords.lon);
  }

  showLoadingState(true);
  try {
    const res = await fetch("/api/classify", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    renderClassificationResult(data);
  } catch (e) {
    alert("Failed to classify image: " + e.message);
  } finally {
    showLoadingState(false);
  }
}

async function classifyBase64(base64Str) {
  showLoadingState(true);
  const formData = new FormData();
  formData.append("image_base64", base64Str);
  if (currentCoords.lat && currentCoords.lon) {
    formData.append("lat", currentCoords.lat);
    formData.append("lon", currentCoords.lon);
  }

  try {
    const res = await fetch("/api/classify", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    renderClassificationResult(data);
  } catch (e) {
    alert("Classification error: " + e.message);
  } finally {
    showLoadingState(false);
  }
}

// One-click Sample Gallery Trigger
window.testSample = async function (categoryName, imageFileName) {
  showLoadingState(true);
  const imgUrl = `/sample-images/${imageFileName}`;
  displayPreview(imgUrl);

  try {
    const resp = await fetch(imgUrl);
    const blob = await resp.blob();
    const file = new File([blob], imageFileName, { type: "image/jpeg" });
    await uploadFileForClassification(file);
  } catch (e) {
    console.error("Sample test error:", e);
  } finally {
    showLoadingState(false);
  }
};

function displayPreview(src) {
  const previewImg = document.getElementById("captured-preview-img");
  const previewContainer = document.getElementById("preview-container");
  if (previewImg && previewContainer) {
    previewImg.src = src;
    previewContainer.classList.remove("hidden");
  }
}

function showLoadingState(isLoading) {
  const spinner = document.getElementById("classification-spinner");
  const resultPanel = document.getElementById("result-panel");
  if (spinner) spinner.classList.toggle("hidden", !isLoading);
  if (isLoading && resultPanel) resultPanel.classList.add("opacity-50");
  else if (resultPanel) resultPanel.classList.remove("opacity-50");
}

// ---------------- Render Results ----------------
function renderClassificationResult(data) {
  currentClassification = data;
  const resPanel = document.getElementById("result-panel");
  if (!resPanel) return;
  resPanel.classList.remove("hidden");

  const pred = data.prediction;
  const guide = data.disposal_guide;

  // 1. Classification Title and Confidence
  document.getElementById("res-waste-icon").textContent = guide.icon || "♻️";
  document.getElementById("res-waste-title").textContent = guide.display_name;
  document.getElementById("res-bin-tag").textContent = guide.bin_name;
  document.getElementById("res-bin-tag").style.backgroundColor = guide.bin_color + "22";
  document.getElementById("res-bin-tag").style.borderColor = guide.bin_color;
  document.getElementById("res-bin-tag").style.color = guide.bin_color;

  const confPercent = pred.confidence_percentage;
  document.getElementById("res-confidence-bar").style.width = `${confPercent}%`;
  document.getElementById("res-confidence-text").textContent = `${confPercent}% Confidence`;

  // 2. Low-Confidence Prompt / 2nd photo trigger
  const lowConfBox = document.getElementById("low-confidence-box");
  if (pred.needs_second_photo) {
    lowConfBox.classList.remove("hidden");
    document.getElementById("low-conf-guidance").textContent = pred.second_photo_guidance;
  } else {
    lowConfBox.classList.add("hidden");
  }

  // 3. Preparation Checklist
  const prepList = document.getElementById("res-prep-steps");
  prepList.innerHTML = "";
  guide.preparation_steps.forEach((step) => {
    const li = document.createElement("li");
    li.className = "flex items-start text-sm text-gray-300 space-x-2";
    li.innerHTML = `
      <span class="text-emerald-400 mt-0.5">✔</span>
      <span>${step}</span>
    `;
    prepList.appendChild(li);
  });

  // 4. Contamination Warnings
  const warnList = document.getElementById("res-warn-steps");
  warnList.innerHTML = "";
  guide.contamination_warnings.forEach((warn) => {
    const li = document.createElement("li");
    li.className = "flex items-start text-sm text-amber-200/90 space-x-2";
    li.innerHTML = `
      <span class="text-amber-400 mt-0.5">⚠</span>
      <span>${warn}</span>
    `;
    warnList.appendChild(li);
  });

  // 5. Quantified Eco Impact
  const impact = guide.environmental_impact;
  document.getElementById("res-co2-val").textContent = `${impact.co2_saved_kg} kg`;
  document.getElementById("res-water-val").textContent = `${impact.water_saved_liters} L`;
  document.getElementById("res-landfill-val").textContent = `${impact.landfill_diverted_grams} g`;
  document.getElementById("res-eco-fact").textContent = guide.eco_fact;

  // 6. Nearest Recycler Teaser
  const mapTeaser = document.getElementById("res-recycler-teaser");
  if (data.recycling_map && data.recycling_map.closest_facility) {
    const facility = data.recycling_map.closest_facility;
    mapTeaser.classList.remove("hidden");
    document.getElementById("teaser-recycler-name").textContent = facility.name;
    document.getElementById("teaser-recycler-dist").textContent = `${facility.distance_km} km away (${facility.walking_time_mins} min walk)`;
    document.getElementById("teaser-recycler-addr").textContent = facility.address;

    // Draw on map directly
    plotRecyclersOnMap(data.recycling_map.facilities, data.recycling_map.route_waypoints);
  } else {
    mapTeaser.classList.add("hidden");
  }

  // Scroll smoothly to results
  resPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ---------------- Map Plotting ----------------
async function fetchNearbyRecyclers(wasteFilter = null) {
  try {
    let url = `/api/recycling-map?lat=${currentCoords.lat}&lon=${currentCoords.lon}&limit=5`;
    if (wasteFilter) url += `&waste_type=${encodeURIComponent(wasteFilter)}`;

    const res = await fetch(url);
    const data = await res.json();
    plotRecyclersOnMap(data.facilities, data.route_waypoints);
    renderRecyclerCards(data.facilities);
  } catch (e) {
    console.error("GIS fetch error:", e);
  }
}

function plotRecyclersOnMap(facilities, routeWaypoints) {
  if (!mapInstance) return;

  // Clear previous markers & route
  recyclerMarkers.forEach((m) => mapInstance.removeLayer(m));
  recyclerMarkers = [];
  if (routePolyline) {
    mapInstance.removeLayer(routePolyline);
    routePolyline = null;
  }

  // Draw facilities
  facilities.forEach((f, idx) => {
    const isClosest = idx === 0;
    const pinColor = isClosest ? "#EF4444" : "#3B82F6";
    const markerIcon = L.divIcon({
      className: "recycler-pin",
      html: `
        <div style="background: ${pinColor}; color: white; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 13px; box-shadow: 0 2px 8px rgba(0,0,0,0.5); border: 2px solid white;">
          ${idx + 1}
        </div>
      `,
      iconSize: [28, 28],
      iconAnchor: [14, 14],
    });

    const popupHtml = `
      <div class="p-1">
        <h4 style="font-weight: 700; font-size: 14px; margin-bottom: 4px;">${f.name}</h4>
        <p style="font-size: 12px; color: #94a3b8; margin-bottom: 4px;">📍 ${f.address}</p>
        <p style="font-size: 12px; margin-bottom: 4px;"><b>Distance:</b> ${f.distance_km} km (${f.walking_time_mins} min walk / ${f.driving_time_mins} min drive)</p>
        <p style="font-size: 11px; color: #10B981;"><b>Accepted:</b> ${f.types.join(", ")}</p>
        <p style="font-size: 11px; color: #cbd5e1; margin-top: 4px;">⏰ ${f.opening_hours}</p>
      </div>
    `;

    const m = L.marker([f.lat, f.lon], { icon: markerIcon }).addTo(mapInstance).bindPopup(popupHtml);
    recyclerMarkers.push(m);
  });

  // Draw route polyline to closest facility
  if (routeWaypoints && routeWaypoints.length > 0) {
    routePolyline = L.polyline(routeWaypoints, {
      color: "#10B981",
      weight: 4,
      dashArray: "6, 8",
      opacity: 0.9,
    }).addTo(mapInstance);
  }
}

function renderRecyclerCards(facilities) {
  const container = document.getElementById("recyclers-list-container");
  if (!container) return;
  container.innerHTML = "";

  if (!facilities || facilities.length === 0) {
    container.innerHTML = `<div class="p-4 text-center text-gray-400">No recycling points found matching this filter.</div>`;
    return;
  }

  facilities.forEach((f, idx) => {
    const card = document.createElement("div");
    card.className = "p-4 glass-panel glass-panel-hover flex flex-col justify-between";
    card.innerHTML = `
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">#${idx + 1} • ${f.distance_km} km</span>
          <span class="text-xs text-gray-400">🚶 ${f.walking_time_mins} mins</span>
        </div>
        <h4 class="font-bold text-gray-100 text-sm mb-1">${f.name}</h4>
        <p class="text-xs text-gray-400 mb-2">${f.address}</p>
        <div class="flex flex-wrap gap-1 mb-2">
          ${f.types.map((t) => `<span class="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded border border-slate-700">${t}</span>`).join("")}
        </div>
      </div>
      <div class="text-[11px] text-gray-400 border-t border-slate-800 pt-2 flex justify-between items-center">
        <span>⏰ ${f.opening_hours}</span>
        <button onclick="focusOnMapPoint(${f.lat}, ${f.lon})" class="text-emerald-400 hover:underline">View on Map</button>
      </div>
    `;
    container.appendChild(card);
  });
}

window.focusOnMapPoint = function (lat, lon) {
  const tabBtn = document.querySelector('[data-tab="tab-map"]');
  if (tabBtn) tabBtn.click();
  setTimeout(() => {
    if (mapInstance) {
      mapInstance.setView([lat, lon], 15);
      recyclerMarkers.forEach((m) => {
        const pos = m.getLatLng();
        if (Math.abs(pos.lat - lat) < 0.0001 && Math.abs(pos.lng - lon) < 0.0001) {
          m.openPopup();
        }
      });
    }
  }, 250);
};

// ---------------- Gamification & User Activity ----------------
async function handleSortConfirmation() {
  if (!currentClassification) return;

  const btn = document.getElementById("confirm-sorted-btn");
  btn.disabled = true;
  btn.innerHTML = `Recording Points...`;

  try {
    const res = await fetch("/api/record-action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: "user_current",
        waste_class: currentClassification.prediction.predicted_class,
        confidence: currentClassification.prediction.confidence,
        photo_notes: "Sorted correctly via Smart Waste Assistant",
      }),
    });
    const result = await res.json();

    playSuccessChime();

    // Show celebratory animation
    const celebration = document.getElementById("points-celebration-toast");
    if (celebration) {
      celebration.textContent = `+${result.points_earned} Green Points Earned! 🌿`;
      celebration.classList.remove("hidden");
      celebration.classList.add("float-score-anim");
      setTimeout(() => {
        celebration.classList.add("hidden");
        celebration.classList.remove("float-score-anim");
      }, 2500);
    }

    // Refresh profile & leaderboard
    await loadUserProfile();
    await loadLeaderboard();

    btn.innerHTML = `✔ Sorted & Credited! (+${result.points_earned} pts)`;
    btn.classList.add("bg-emerald-600");
  } catch (e) {
    alert("Error logging action: " + e.message);
    btn.disabled = false;
    btn.innerHTML = `I Disposed of This Correctly!`;
  }
}

async function loadUserProfile() {
  try {
    const res = await fetch("/api/user/profile?user_id=user_current");
    const data = await res.json();

    document.getElementById("user-score-display").textContent = data.user.green_score;
    document.getElementById("user-streak-display").textContent = `${data.user.current_streak} Days`;
    document.getElementById("user-items-display").textContent = data.user.items_sorted;

    // Badges render
    const badgesContainer = document.getElementById("user-badges-list");
    if (badgesContainer) {
      badgesContainer.innerHTML = "";
      if (data.badges.length === 0) {
        badgesContainer.innerHTML = `<span class="text-xs text-gray-500">No badges unlocked yet. Sort waste items to unlock awards!</span>`;
      } else {
        data.badges.forEach((b) => {
          const badgeDiv = document.createElement("div");
          badgeDiv.className = "p-3 glass-panel flex items-center space-x-3 border-emerald-500/20";
          badgeDiv.innerHTML = `
            <div class="text-2xl">${b.badge_icon}</div>
            <div>
              <div class="font-bold text-xs text-emerald-400">${b.badge_name}</div>
              <div class="text-[11px] text-gray-400">${b.description}</div>
              <div class="text-[9px] text-gray-500">Unlocked ${b.awarded_at}</div>
            </div>
          `;
          badgesContainer.appendChild(badgeDiv);
        });
      }
    }

    // Cumulative savings
    document.getElementById("stats-co2-total").textContent = `${data.cumulative_impact.total_co2_kg} kg`;
    document.getElementById("stats-water-total").textContent = `${data.cumulative_impact.total_water_liters} L`;
    document.getElementById("stats-landfill-total").textContent = `${data.cumulative_impact.total_landfill_kg} kg`;
  } catch (e) {
    console.error("Profile load error:", e);
  }
}

async function loadLeaderboard() {
  try {
    const res = await fetch("/api/leaderboard?limit=5");
    const data = await res.json();
    const tbody = document.getElementById("leaderboard-body");
    if (!tbody) return;
    tbody.innerHTML = "";

    data.leaderboard.forEach((user) => {
      const tr = document.createElement("tr");
      tr.className = "border-b border-slate-800 text-xs";
      const rankEmoji = user.rank === 1 ? "🥇" : user.rank === 2 ? "🥈" : user.rank === 3 ? "🥉" : `#${user.rank}`;
      tr.innerHTML = `
        <td class="py-2.5 font-bold">${rankEmoji}</td>
        <td class="py-2.5 font-medium text-gray-200">${user.username}</td>
        <td class="py-2.5 font-bold text-emerald-400">${user.green_score} pts</td>
        <td class="py-2.5 text-amber-400">🔥 ${user.streak}</td>
        <td class="py-2.5 text-gray-400">${user.items_sorted}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error("Leaderboard load error:", e);
  }
}
