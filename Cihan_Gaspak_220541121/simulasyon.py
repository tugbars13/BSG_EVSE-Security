from flask import Flask, request, jsonify, render_template_string
import threading
import time
from datetime import datetime
from collections import deque

app = Flask(__name__)

state = {
    "charging": False,
    "charging_current_A": 16.0,
    "humidity_rh": 40.0,
    "water_ingress_level": 0.0,
    "temperature_c": 25.0,
    "insulation_kohm": 1000.0,
    "leakage_mA": 0.0,
    "ip_breach": False,
    "rcd_tripped": False,
    "anomaly_mode": False,
    "last_update": None,
    "humidity_trip_rh": 85.0,
    "insulation_min_kohm": 200.0,
    "leakage_trip_mA": 30.0,
    "water_trip_level": 0.3
}

state_lock = threading.Lock()
stop_threads = False

LOG_FILE = "humidity_water_anomaly_log.txt"
log_seq = 0
recent_logs = deque(maxlen=400)  # (seq, line)

# küçük trend için geçmiş
history = deque(maxlen=120)  # ~son 2-3 dk

def log_event(text):
    global log_seq
    ts = datetime.utcnow().isoformat()
    line = f"{ts} - {text}"
    log_seq += 1
    recent_logs.append((log_seq, line))
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def compute_physics():
    with state_lock:
        humidity = state["humidity_rh"]
        water = state["water_ingress_level"]
        current = state["charging_current_A"]

    base_ins_kohm = 1000.0
    humidity_factor = 1.0 + 3.0 * (humidity / 100.0) ** 3
    water_factor = 1.0 + 10.0 * water

    insulation = base_ins_kohm / (humidity_factor * water_factor)
    leakage = (current * 1000.0) / max(insulation, 1.0)

    with state_lock:
        state["insulation_kohm"] = round(insulation, 2)
        state["leakage_mA"] = round(leakage, 2)
        state["ip_breach"] = (water >= state["water_trip_level"])

def protection_logic():
    with state_lock:
        charging = state["charging"]
        anomaly_mode = state["anomaly_mode"]
        humidity = state["humidity_rh"]
        insulation = state["insulation_kohm"]
        leakage = state["leakage_mA"]
        ip_breach = state["ip_breach"]
        hum_trip = state["humidity_trip_rh"]
        ins_min = state["insulation_min_kohm"]
        leak_trip = state["leakage_trip_mA"]
        water_level = state["water_ingress_level"]

    if not charging:
        return

    danger = (
        humidity >= hum_trip or
        insulation <= ins_min or
        leakage >= leak_trip or
        ip_breach
    )

    if danger:
        if anomaly_mode:
            log_event(
                "ANOMALY: high humidity/water but charging CONTINUES | "
                f"humidity={humidity}, water={water_level}, "
                f"insulation_kohm={insulation}, leakage_mA={leakage}, ip_breach={ip_breach}"
            )
        else:
            with state_lock:
                state["charging"] = False
                state["rcd_tripped"] = True
            log_event(
                "INFO: protection TRIPPED -> charging stopped | "
                f"humidity={humidity}, water={water_level}, "
                f"insulation_kohm={insulation}, leakage_mA={leakage}, ip_breach={ip_breach}"
            )

def watchdog_loop():
    global stop_threads
    while not stop_threads:
        time.sleep(1)
        compute_physics()
        protection_logic()
        with state_lock:
            state["last_update"] = datetime.utcnow()
            history.append({
                "t": state["last_update"].isoformat(timespec="seconds"),
                "ins": state["insulation_kohm"],
                "leak": state["leakage_mA"],
                "hum": state["humidity_rh"],
                "wat": state["water_ingress_level"],
                "chg": state["charging"]
            })

def start_watchdog_thread():
    t = threading.Thread(target=watchdog_loop, daemon=True)
    t.start()

HTML_PAGE = """
<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Nem / Su Teması EV Şarj Simülatörü</title>
<style>
:root{
  --bg:#0b0f19; --panel:#141a2a; --panel2:#0f1422; --ink:#e6e8ef;
  --muted:#9aa3b2; --ok:#22c55e; --bad:#ef4444; --warn:#f59e0b; --info:#3b82f6;
  --line:#222b44; --radius:14px;
}
*{box-sizing:border-box;}
body{font-family:system-ui,Segoe UI,Arial,sans-serif;margin:18px;background:var(--bg);color:var(--ink);}
h1{margin:0 0 4px 0;font-size:22px;}
small{color:var(--muted);}
.grid{
  display:grid; gap:12px;
  grid-template-columns: 320px 1fr 420px;
}
@media (max-width:1100px){ .grid{grid-template-columns: 1fr;} }
.card{
  background:var(--panel); padding:14px; border-radius:var(--radius);
  box-shadow:0 0 0 1px var(--line) inset;
}
.card h3{margin:0 0 10px 0; font-size:15px; color:#cbd5e1; letter-spacing:.2px;}
.btn{padding:8px 12px;border:none;border-radius:10px;cursor:pointer;font-weight:600;color:#0b0f19}
.btn.start{background:var(--ok);} .btn.stop{background:var(--bad);}
.btn.reset{background:var(--warn);} .btn.anom{background:var(--info); color:white;}
.btn:active{transform:translateY(1px);}
.row{display:flex;gap:8px;flex-wrap:wrap;}
label{display:flex;justify-content:space-between;margin-top:10px;color:var(--muted);font-size:13px;}
input[type=range]{width:100%;}
.value{color:var(--ink);font-weight:700;}
.kpi{
  display:grid; grid-template-columns: repeat(3,1fr); gap:8px; margin-top:6px;
}
.kpi .box{
  background:var(--panel2); padding:10px;border-radius:12px;border:1px solid var(--line);
}
.kpi .title{font-size:12px;color:var(--muted);}
.kpi .big{font-size:20px;font-weight:800;margin-top:2px;}
.badge{
  display:inline-flex; align-items:center; gap:6px;
  padding:4px 8px; border-radius:999px; font-size:12px; font-weight:700;
}
.badge.ok{background:rgba(34,197,94,.15); color:var(--ok); border:1px solid rgba(34,197,94,.35);}
.badge.bad{background:rgba(239,68,68,.15); color:var(--bad); border:1px solid rgba(239,68,68,.35);}
.split{display:flex;justify-content:space-between;align-items:center;gap:8px;}
.hr{height:1px;background:var(--line);margin:10px 0;}
.logbox{
  height:330px; overflow:auto; font-size:12.5px; line-height:1.35;
  background:var(--panel2); padding:10px; border-radius:12px;border:1px solid var(--line);
  white-space:pre-wrap;
}
.logline.anom{color:#fca5a5;} .logline.info{color:#93c5fd;}
canvas{width:100%;height:160px;background:var(--panel2);border-radius:12px;border:1px solid var(--line);}
.legend{display:flex;gap:10px;font-size:12px;color:var(--muted);margin-top:6px;}
.legend span{display:inline-flex;align-items:center;gap:6px;}
.dot{width:8px;height:8px;border-radius:999px;display:inline-block;}
.dot.ins{background:var(--ok);} .dot.leak{background:var(--warn);}
</style>
</head>
<body>
  <div class="split">
    <div>
      <h1>Nem / Su Teması EV Şarj Simülatörü</h1>
      <small>Canlı durum, trendler ve anomali logları</small>
    </div>
    <div id="lastUpdate" style="font-size:12px;color:var(--muted)"></div>
  </div>

  <div class="grid">
    <div class="card">
      <h3>Kontroller</h3>
      <div class="row">
        <button class="btn start" onclick="startCharge()">Şarj Başlat</button>
        <button class="btn stop" onclick="stopCharge()">Şarj Durdur</button>
        <button class="btn reset" onclick="resetProtection()">RCD Reset</button>
      </div>

      <label>Akım (A) <span class="value" id="curVal">16</span></label>
      <input id="cur" type="range" min="6" max="64" step="1" value="16">
      
      <label>Nem (%RH) <span class="value" id="humVal">40</span></label>
      <input id="hum" type="range" min="0" max="100" step="1" value="40">

      <label>Su Girişi (0-1) <span class="value" id="watVal">0.00</span></label>
      <input id="wat" type="range" min="0" max="1" step="0.01" value="0">

      <div class="hr"></div>

      <div class="row">
        <button class="btn anom" onclick="toggleAnomaly()">
          Anomali Modu: <span id="anomText">OFF</span>
        </button>
      </div>

      <div style="margin-top:10px;font-size:12px;color:var(--muted);">
        Normal modda eşik aşılınca koruma şarjı keser.  
        Anomali modunda şarj devam eder ve log düşer.
      </div>
    </div>

    <div class="card">
      <h3>Canlı Durum</h3>
      <div class="row" style="gap:6px;">
        <span id="bCharging" class="badge">-</span>
        <span id="bIp" class="badge">-</span>
        <span id="bRcd" class="badge">-</span>
      </div>

      <div class="kpi">
        <div class="box">
          <div class="title">İzolasyon (kΩ)</div>
          <div id="ins" class="big">-</div>
        </div>
        <div class="box">
          <div class="title">Kaçak Akım (mA)</div>
          <div id="leak" class="big">-</div>
        </div>
        <div class="box">
          <div class="title">Nem / Su</div>
          <div class="big"><span id="humKpi">-</span>% / <span id="watKpi">-</span></div>
        </div>
      </div>

      <div class="hr"></div>
      <h3 style="margin-top:2px;">Son Trend (yaklaşık 2 dk)</h3>
      <canvas id="chart" width="600" height="200"></canvas>
      <div class="legend">
        <span><i class="dot ins"></i> İzolasyon</span>
        <span><i class="dot leak"></i> Kaçak Akım</span>
      </div>
      <small id="thresholdNote"></small>
    </div>

    <div class="card">
      <h3>Log Akışı (delta)</h3>
      <div id="logs" class="logbox"></div>
    </div>
  </div>

<script>
let anomalyMode = false;
let logSince = 0;
let hist = [];
let envTimer = null;
let curTimer = null;

function badge(el, text, type){
  el.textContent = text;
  el.className = "badge " + type;
}

async function startCharge(){ await fetch(`/start_charge`, {method:"POST"}); }
async function stopCharge(){ await fetch(`/stop_charge`, {method:"POST"}); }
async function resetProtection(){ await fetch(`/reset_protection`, {method:"POST"}); }

async function setCurrent(v){
  document.getElementById("curVal").textContent = v;
  await fetch(`/set_current?current_A=${v}`, {method:"POST"});
}
async function setEnv(h, w){
  await fetch(`/set_env?humidity_rh=${h}&water_level=${w}`, {method:"POST"});
}

function toggleAnomaly(){
  anomalyMode = !anomalyMode;
  fetch(`/set_anomaly?mode=${anomalyMode ? "on":"off"}`, {method:"POST"});
  document.getElementById("anomText").textContent = anomalyMode ? "ON":"OFF";
}

function drawChart(){
  const canvas = document.getElementById("chart");
  const ctx = canvas.getContext("2d");
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0,0,W,H);
  if(hist.length < 2) return;

  const insVals = hist.map(p => p.ins);
  const leakVals = hist.map(p => p.leak);
  const insMin = Math.min(...insVals), insMax = Math.max(...insVals);
  const leakMin = Math.min(...leakVals), leakMax = Math.max(...leakVals);

  function x(i){ return (i/(hist.length-1))* (W-30) + 20; }
  function yIns(v){
    const t = (v - insMin) / (insMax - insMin + 1e-6);
    return H - (t*(H-30) + 15);
  }
  function yLeak(v){
    const t = (v - leakMin) / (leakMax - leakMin + 1e-6);
    return H - (t*(H-30) + 15);
  }

  ctx.globalAlpha = 0.25;
  ctx.beginPath();
  for(let gy=15; gy<=H-15; gy+= (H-30)/4){
    ctx.moveTo(20, gy); ctx.lineTo(W-10, gy);
  }
  ctx.strokeStyle = "#46516e"; ctx.stroke();
  ctx.globalAlpha = 1;

  ctx.beginPath();
  hist.forEach((p,i)=>{
    const xx=x(i), yy=yIns(p.ins);
    if(i===0) ctx.moveTo(xx,yy); else ctx.lineTo(xx,yy);
  });
  ctx.strokeStyle = "#22c55e"; ctx.lineWidth = 2; ctx.stroke();

  ctx.beginPath();
  hist.forEach((p,i)=>{
    const xx=x(i), yy=yLeak(p.leak);
    if(i===0) ctx.moveTo(xx,yy); else ctx.lineTo(xx,yy);
  });
  ctx.strokeStyle = "#f59e0b"; ctx.lineWidth = 2; ctx.stroke();
}

async function refreshStatus(){
  const s = await (await fetch("/status")).json();
  anomalyMode = s.anomaly_mode;

  badge(document.getElementById("bCharging"), s.charging ? "ŞARJ ON" : "ŞARJ OFF", s.charging ? "ok":"bad");
  badge(document.getElementById("bIp"), s.ip_breach ? "IP BREACH" : "IP OK", s.ip_breach ? "bad":"ok");
  badge(document.getElementById("bRcd"), s.rcd_tripped ? "RCD TRIPPED" : "RCD OK", s.rcd_tripped ? "bad":"ok");

  document.getElementById("ins").textContent = s.insulation_kohm;
  document.getElementById("leak").textContent = s.leakage_mA;
  document.getElementById("humKpi").textContent = s.humidity_rh;
  document.getElementById("watKpi").textContent = s.water_ingress_level.toFixed(2);
  document.getElementById("anomText").textContent = anomalyMode ? "ON":"OFF";

  const cur = document.getElementById("cur");
  const hum = document.getElementById("hum");
  const wat = document.getElementById("wat");
  if(!cur.matches(":active")) cur.value = s.current_A;
  if(!hum.matches(":active")) hum.value = s.humidity_rh;
  if(!wat.matches(":active")) wat.value = s.water_ingress_level;

  document.getElementById("curVal").textContent = s.current_A;
  document.getElementById("humVal").textContent = s.humidity_rh;
  document.getElementById("watVal").textContent = s.water_ingress_level.toFixed(2);
  document.getElementById("lastUpdate").textContent = "Son güncelleme: " + s.last_update;

  document.getElementById("thresholdNote").textContent =
    `Eşikler → Nem ≥ ${s.thresholds.humidity_trip_rh}% | İzolasyon ≤ ${s.thresholds.insulation_min_kohm}kΩ | Kaçak ≥ ${s.thresholds.leakage_trip_mA}mA | Su ≥ ${s.thresholds.water_trip_level}`;
}

async function refreshHistory(){
  hist = (await (await fetch("/history")).json()).points;
  drawChart();
}

async function refreshLogs(){
  const data = await (await fetch(`/log?since=${logSince}`)).json();
  logSince = data.next_since;

  if(data.lines.length){
    const box = document.getElementById("logs");
    data.lines.forEach(l=>{
      const div = document.createElement("div");
      div.className = "logline " + (l.includes("ANOMALY") ? "anom":"info");
      div.textContent = l;
      box.appendChild(div);
    });
    while(box.children.length > 300) box.removeChild(box.firstChild);
    box.scrollTop = box.scrollHeight;
  }
}

document.getElementById("hum").addEventListener("input", (e)=>{
  document.getElementById("humVal").textContent = e.target.value;
  clearTimeout(envTimer);
  envTimer = setTimeout(()=>{
    setEnv(document.getElementById("hum").value, document.getElementById("wat").value);
  }, 180);
});
document.getElementById("wat").addEventListener("input", (e)=>{
  document.getElementById("watVal").textContent = parseFloat(e.target.value).toFixed(2);
  clearTimeout(envTimer);
  envTimer = setTimeout(()=>{
    setEnv(document.getElementById("hum").value, document.getElementById("wat").value);
  }, 180);
});
document.getElementById("cur").addEventListener("input", (e)=>{
  document.getElementById("curVal").textContent = e.target.value;
  clearTimeout(curTimer);
  curTimer = setTimeout(()=> setCurrent(e.target.value), 220);
});

setInterval(refreshStatus, 1500);
setInterval(refreshLogs, 2200);
setInterval(refreshHistory, 3000);
refreshStatus(); refreshLogs(); refreshHistory();
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/log")
def get_log():
    since = request.args.get("since", default=0, type=int)
    items = list(recent_logs)
    if not items:
        return jsonify({"lines": [], "next_since": since})
    oldest_seq = items[0][0]
    newest_seq = items[-1][0]
    if since < oldest_seq:
        lines = [line for (_, line) in items]
    else:
        lines = [line for (seq, line) in items if seq > since]
    return jsonify({"lines": lines, "next_since": newest_seq})

@app.route("/history")
def get_history():
    return jsonify({"points": list(history)})

@app.route("/start_charge", methods=["POST"])
def start_charge():
    with state_lock:
        state["charging"] = True
        state["rcd_tripped"] = False
        state["last_update"] = datetime.utcnow()
    log_event("INFO: charging started")
    return jsonify({"status":"charging_started"})

@app.route("/stop_charge", methods=["POST"])
def stop_charge():
    with state_lock:
        state["charging"] = False
        state["last_update"] = datetime.utcnow()
    log_event("INFO: charging stopped")
    return jsonify({"status":"charging_stopped"})

@app.route("/set_current", methods=["POST"])
def set_current():
    current = request.args.get("current_A", type=float)
    if current is None:
        return jsonify({"error":"current_A required"}), 400
    with state_lock:
        state["charging_current_A"] = max(0.0, current)
        state["last_update"] = datetime.utcnow()
    return jsonify({"status":"current_updated", "current_A": state["charging_current_A"]})

@app.route("/set_env", methods=["POST"])
def set_env():
    humidity = request.args.get("humidity_rh", type=float)
    water = request.args.get("water_level", type=float)
    temp = request.args.get("temp_c", type=float)
    with state_lock:
        if humidity is not None:
            state["humidity_rh"] = max(0.0, min(100.0, humidity))
        if water is not None:
            state["water_ingress_level"] = max(0.0, min(1.0, water))
        if temp is not None:
            state["temperature_c"] = temp
        state["last_update"] = datetime.utcnow()
    return jsonify({"status":"env_updated"})

@app.route("/set_anomaly", methods=["POST"])
def set_anomaly():
    mode = request.args.get("mode","off").lower()
    with state_lock:
        state["anomaly_mode"] = (mode == "on")
        state["last_update"] = datetime.utcnow()
    log_event(f"INFO: anomaly_mode set to {state['anomaly_mode']}")
    return jsonify({"anomaly_mode": state["anomaly_mode"]})

@app.route("/reset_protection", methods=["POST"])
def reset_protection():
    with state_lock:
        state["rcd_tripped"] = False
        state["last_update"] = datetime.utcnow()
    log_event("INFO: RCD reset")
    return jsonify({"status":"protection_reset"})

@app.route("/status")
def status():
    with state_lock:
        last = state["last_update"].isoformat() if state["last_update"] else None
        return jsonify({
            "charging": state["charging"],
            "current_A": state["charging_current_A"],
            "humidity_rh": state["humidity_rh"],
            "water_ingress_level": state["water_ingress_level"],
            "temperature_c": state["temperature_c"],
            "insulation_kohm": state["insulation_kohm"],
            "leakage_mA": state["leakage_mA"],
            "ip_breach": state["ip_breach"],
            "rcd_tripped": state["rcd_tripped"],
            "anomaly_mode": state["anomaly_mode"],
            "thresholds": {
                "humidity_trip_rh": state["humidity_trip_rh"],
                "insulation_min_kohm": state["insulation_min_kohm"],
                "leakage_trip_mA": state["leakage_trip_mA"],
                "water_trip_level": state["water_trip_level"]
            },
            "last_update": last
        })

if __name__ == "__main__":
    try:
        start_watchdog_thread()
        print("🚀 Nem/Su Teması EV Şarj Simülatörü başlatılıyor...")
        print("📡 Panel: http://127.0.0.1:5000")
        app.run(host="0.0.0.0", port=5000, debug=True)
    finally:
        stop_threads = True
