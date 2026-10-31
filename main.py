"""
BITCOIN DAILY INTELLIGENCE REPORT
Run daily for a risk-scored trading bias on BTC/USD.
Data sources: Yahoo Finance, with fallbacks to last-known values.
Output: colorful HTML report -> index.html
"""

import json
import urllib.request
from datetime import datetime, timezone

def fetch_json(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None

def get_price(symbol, fallback):
    data = fetch_json(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d")
    if data and 'chart' in data and data['chart']['result']:
        return data['chart']['result'][0]['meta'].get('regularMarketPrice', fallback)
    return fallback

btc    = get_price("BTC-USD",  95000.00)
eth    = get_price("ETH-USD",   3500.00)
dxy    = get_price("DX-Y.NYB",   102.15)
nasdaq = get_price("^IXIC",    19500.00)

eth_btc_ratio = eth / btc if btc else 0.037

levels = {
    "R2": 99500.00, "R1": 97800.00, "R0": 96500.00,
    "Pivot": 95000.00,
    "S1": 93500.00, "S2": 92000.00, "S3": 90000.00,
}

sentiment = {
    "fear_greed": "Greed",
    "trend_strength": 8,
    "bull_probability": 65,
    "bear_probability": 35,
    "funding_rate": "Positive (Bullish)",
}

def compute_score():
    score = 0
    factors = []
    pivot = levels["Pivot"]
    
    if btc > pivot + 500:
        score += 15; factors.append(("Price vs Pivot", f"{btc:.0f} > {pivot:.0f}", "Above pivot — bullish momentum", 15))
    elif btc < pivot - 500:
        score -= 15; factors.append(("Price vs Pivot", f"{btc:.0f} < {pivot:.0f}", "Below pivot — bearish pressure", -15))
    else:
        factors.append(("Price vs Pivot", f"{btc:.0f} ≈ {pivot:.0f}", "At pivot", 0))

    if dxy > 103:
        score -= 10; factors.append(("DXY (Dollar)", f"{dxy:.2f}", "Strong dollar — crypto headwind", -10))
    elif dxy < 99:
        score += 10; factors.append(("DXY (Dollar)", f"{dxy:.2f}", "Weak dollar — crypto tailwind", 10))
    else:
        factors.append(("DXY (Dollar)", f"{dxy:.2f}", "Neutral", 0))

    score = max(-100, min(100, score))
    action = "BUY" if score >= 15 else ("SELL" if score <= -15 else "WAIT")
    confidence = min(100, abs(score) + 25)

    if action == "BUY":
        entry, stop, target = levels["S1"], levels["S2"] - 1000, levels["R1"]
    elif action == "SELL":
        entry, stop, target = levels["R0"], levels["R2"] + 1000, levels["S1"]
    else:
        entry, stop, target = btc, 0, 0

    risk = abs(entry - stop) if action == "BUY" else abs(stop - entry)
    reward = abs(target - entry) if action == "BUY" else abs(entry - target)
    rr = round(reward / risk, 2) if risk > 0 else 0

    return {"score": score, "action": action, "confidence": confidence,
            "rr": rr, "entry": entry, "stop": stop, "target": target, "factors": factors}

result = compute_score()

def build_html():
    a = result["action"]
    color = {"BUY": "#00c853", "SELL": "#d50000", "WAIT": "#ff9100"}.get(a, "#9e9e9e")

    factor_rows = ""
    for name, value, desc, contrib in result["factors"]:
        c = "#00c853" if contrib > 0 else ("#d50000" if contrib < 0 else "#9e9e9e")
        sign = "+" if contrib > 0 else ""
        factor_rows += f"<tr><td><b>{name}</b></td><td>{value}</td><td>{desc}</td><td style='color:{c};font-weight:bold'>{sign}{contrib}</td></tr>"

    level_rows = ""
    for k, v in levels.items():
        dist = ((v - btc) / btc) * 100
        level_rows += f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{dist:+.2f}%</td></tr>"

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>Bitcoin Intelligence Report {datetime.now(timezone.utc).strftime('%Y-%m-%d')}</title>
<style>
body{{font-family:'Segoe UI',Arial,sans-serif;background:#0d1117;color:#e6edf3;padding:20px}}
.container{{max-width:960px;margin:auto}}
h1{{color:#f7931a;text-align:center}}
h2{{color:#58a6ff;border-bottom:1px solid #30363d;padding-bottom:6px}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:20px;margin:16px 0}}
.action-box{{text-align:center;padding:24px;border-radius:12px;background:{color}22;border:2px solid {color}}}
.action-label{{font-size:48px;font-weight:bold;color:{color}}}
table{{width:100%;border-collapse:collapse;margin-top:8px}}
th{{text-align:left;color:#8b949e;border-bottom:1px solid #30363d;padding:8px 4px}}
td{{padding:8px 4px;border-bottom:1px solid #21262d}}
.metric{{display:inline-block;margin:8px 16px;text-align:center}}
.val{{font-size:22px;font-weight:bold;color:#f7931a}}
.lbl{{font-size:12px;color:#8b949e}}
.footer{{text-align:center;color:#8b949e;font-size:12px;margin-top:32px}}
</style></head><body><div class="container">
<h1>₿ Bitcoin Autonomous Intelligence Report</h1>
<p style="text-align:center;color:#8b949e">{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · BTC/USD</p>

<div class="card action-box">
  <div class="action-label">{a}</div>
  <p>Score: <b>{result['score']}</b>/100 · Confidence: <b>{result['confidence']}%</b> · R:R: <b>{result['rr']}:1</b></p>
</div>

<div class="card"><h2>📊 Market Snapshot</h2>
<div style="display:flex;flex-wrap:wrap;justify-content:space-around">
  <div class="metric"><div class="val">${btc:,.2f}</div><div class="lbl">Bitcoin</div></div>
  <div class="metric"><div class="val">${eth:,.2f}</div><div class="lbl">Ethereum</div></div>
  <div class="metric"><div class="val">{eth_btc_ratio:.3f}</div><div class="lbl">ETH/BTC</div></div>
  <div class="metric"><div class="val">{dxy:.2f}</div><div class="lbl">DXY</div></div>
  <div class="metric"><div class="val">${nasdaq:,.0f}</div><div class="lbl">Nasdaq</div></div>
</div></div>

<div class="card"><h2>🧮 Factor Scorecard</h2>
<table><tr><th>Factor</th><th>Value</th><th>Interpretation</th><th>Score</th></tr>{factor_rows}</table></div>

<div class="card"><h2>📍 Key Levels</h2>
<table><tr><th>Level</th><th>Price</th><th>Distance</th></tr>{level_rows}</table></div>

<div class="card"><h2>🎯 Trade Plan</h2>
<table>
<tr><td>Direction</td><td style="color:{color};font-weight:bold">{a}</td></tr>
<tr><td>Entry</td><td>${result['entry']:,.2f}</td></tr>
<tr><td>Stop Loss</td><td>${result['stop']:,.2f}</td></tr>
<tr><td>Take Profit</td><td>${result['target']:,.2f}</td></tr>
<tr><td>Risk/Reward</td><td>{result['rr']}:1</td></tr>
</table></div>

<div class="footer"><p>⚠️ Educational only. Not financial advice.</p></div>
</div></body></html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(build_html())

print("Report generated successfully.")
