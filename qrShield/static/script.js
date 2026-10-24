const $ = (id) => document.getElementById(id);
let current = null;

function setResult(state, title, msg) {
  $("result").className = "result " + state;
  $("resTitle").textContent = title;
  $("resMsg").textContent = msg;
}

function markModified() {
  $("payload").classList.toggle("modified", current && $("payload").value !== current.data);
}

async function generate() {
  const user = $("user").value.trim() || "Authorized User";
  $("genBtn").disabled = true;
  try {
    const res = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user }),
    });
    current = await res.json();
  } catch (e) {
    setResult("bad", "Server not reachable", "Make sure main.py is running, then try again.");
    $("genBtn").disabled = false;
    return;
  }

  $("qrImg").src = "data:image/png;base64," + current.qr_image;
  $("qrImg").hidden = false;
  $("qrEmpty").hidden = true;
  $("fUser").textContent = current.user;
  $("fToken").textContent = current.token;
  $("fAlgo").textContent = current.algorithm;
  $("fSig").textContent = current.signature;

  $("payload").disabled = false;
  $("payload").value = current.data;
  ["verBtn", "tamperBtn", "resetBtn", "dlBtn"].forEach((id) => ($(id).disabled = false));
  markModified();
  setResult("idle", "Not checked yet", "Press Verify signature to check this token.");

  const scan = $("scan");
  scan.classList.remove("run");
  void scan.offsetWidth; // restart animation
  scan.classList.add("run");
  $("genBtn").disabled = false;
}

async function verify() {
  if (!current) return;
  setResult("idle", "Checking...", "Comparing the data with its signature.");
  try {
    const res = await fetch("/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        authentication_data: $("payload").value,
        signature: current.signature,
      }),
    });
    const out = await res.json();
    if (out.valid) {
      setResult("ok", "Access granted", "The signature matches. This data came from the key holder and has not changed.");
    } else {
      setResult("bad", "Access denied", "The signature does not match this data. It was forged or edited after signing.");
    }
  } catch (e) {
    setResult("bad", "Server not reachable", "Make sure main.py is running, then try again.");
  }
}

function tamper() {
  if (!current) return;
  $("payload").value = current.data.replace("ACCESS=AUTHORIZED", "ACCESS=ADMIN");
  markModified();
  verify();
}

function reset() {
  if (!current) return;
  $("payload").value = current.data;
  markModified();
  setResult("idle", "Not checked yet", "Original data restored. Verify it again.");
}

function download() {
  if (!current) return;
  const a = document.createElement("a");
  a.href = "data:image/png;base64," + current.qr_image;
  a.download = current.token + ".png";
  a.click();
}

$("genBtn").addEventListener("click", generate);
$("verBtn").addEventListener("click", verify);
$("tamperBtn").addEventListener("click", tamper);
$("resetBtn").addEventListener("click", reset);
$("dlBtn").addEventListener("click", download);
$("payload").addEventListener("input", markModified);
$("user").addEventListener("keydown", (e) => { if (e.key === "Enter") generate(); });
