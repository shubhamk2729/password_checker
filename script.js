const passwordInput = document.getElementById("password-input");
const toggleBtn = document.getElementById("toggle-visibility");
const meterFill = document.getElementById("meter-fill");
const meterScore = document.getElementById("meter-score");
const ratingText = document.getElementById("rating-text");
const notesPanel = document.getElementById("notes-panel");
const notesList = document.getElementById("notes-list");
const breachButton = document.getElementById("breach-button");
const stampZone = document.getElementById("stamp-zone");

let debounceTimer = null;

toggleBtn.addEventListener("click", () => {
  const isHidden = passwordInput.type === "password";
  passwordInput.type = isHidden ? "text" : "password";
  toggleBtn.textContent = isHidden ? "🙈" : "👁";
  toggleBtn.setAttribute("aria-label", isHidden ? "Hide password" : "Show password");
});

passwordInput.addEventListener("input", () => {
  const password = passwordInput.value;
  breachButton.disabled = password.length === 0;
  stampZone.innerHTML = "";

  clearTimeout(debounceTimer);

  if (!password) {
    resetReadout();
    return;
  }

  debounceTimer = setTimeout(() => checkStrength(password), 250);
});

async function checkStrength(password) {
  try {
    const res = await fetch("/api/strength", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });
    if (!res.ok) return;
    const data = await res.json();
    renderStrength(data);
  } catch (err) {
    console.error("Strength check failed:", err);
  }
}

function renderStrength(data) {
  // Meter
  meterFill.style.width = data.score + "%";
  meterFill.style.backgroundColor = colorForScore(data.score);
  meterScore.textContent = data.score + " / 100";
  ratingText.textContent = "Rating: " + data.rating.toUpperCase();

  // Readout rows
  setRow("length", data.length + " chars", flagFor(data.length >= 12, data.length >= 8));
  setRow("variety", data.variety_count + "/4 classes", flagFor(data.variety_count === 4, data.variety_count === 3));
  setRow("entropy", data.entropy_bits + " bits", flagFor(data.entropy_bits >= 60, data.entropy_bits >= 28));

  const patternHit = data.has_sequential || data.has_repeated || data.has_keyboard_pattern;
  setRow("pattern", patternHit ? "pattern detected" : "clear", flagFor(!patternHit, false));

  setRow("known", data.is_known_common ? "match found" : "no match", flagFor(!data.is_known_common, false));

  // Field notes
  notesList.innerHTML = "";
  data.feedback.forEach((note) => {
    const li = document.createElement("li");
    li.textContent = note;
    notesList.appendChild(li);
  });
  notesPanel.hidden = false;
}

function setRow(test, value, flagClass) {
  document.getElementById("v-" + test).textContent = value;
  const flagEl = document.getElementById("f-" + test);
  flagEl.className = "t-flag " + flagClass.cls;
  flagEl.textContent = flagClass.symbol;
}

function flagFor(pass, warnOk) {
  if (pass) return { cls: "flag-pass", symbol: "✓" };
  if (warnOk) return { cls: "flag-warn", symbol: "!" };
  return { cls: "flag-fail", symbol: "✕" };
}

function colorForScore(score) {
  if (score >= 60) return "#66C7CE"; // signal-cyan
  if (score >= 30) return "#E2622E"; // signal-orange
  return "#C94A3B"; // fail-line
}

function resetReadout() {
  meterFill.style.width = "0%";
  meterScore.textContent = "—";
  ratingText.textContent = "Awaiting specimen";
  ["length", "variety", "entropy", "pattern", "known"].forEach((t) => {
    document.getElementById("v-" + t).textContent = "—";
    const f = document.getElementById("f-" + t);
    f.className = "t-flag";
    f.textContent = "—";
  });
  notesPanel.hidden = true;
}

breachButton.addEventListener("click", async () => {
  const password = passwordInput.value;
  if (!password) return;

  breachButton.disabled = true;
  breachButton.textContent = "Scanning...";
  stampZone.innerHTML = "";

  try {
    const res = await fetch("/api/breach", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });
    const data = await res.json();

    if (data.error) {
      stampZone.innerHTML = `<span style="font-family: var(--font-mono); font-size: 13px; color: #C94A3B;">${data.error}</span>`;
    } else if (data.breached) {
      const stamp = document.createElement("div");
      stamp.className = "stamp stamp-flagged";
      stamp.textContent = `FLAGGED — ${data.count.toLocaleString()} BREACHES`;
      stampZone.appendChild(stamp);
    } else {
      const stamp = document.createElement("div");
      stamp.className = "stamp stamp-clear";
      stamp.textContent = "CLEAR";
      stampZone.appendChild(stamp);
    }
  } catch (err) {
    stampZone.innerHTML = `<span style="font-family: var(--font-mono); font-size: 13px; color: #C94A3B;">Could not reach breach database.</span>`;
  } finally {
    breachButton.disabled = false;
    breachButton.textContent = "Run Field Inspection";
  }
});
