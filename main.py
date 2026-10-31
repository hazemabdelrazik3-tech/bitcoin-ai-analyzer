"""
BITCOIN INSTITUTIONAL MASTER INTELLIGENCE SUITE
Run daily for a risk-scored trading bias on BTC/USD with dynamic levels.
Data sources: Yahoo Finance & Live Feeds.
Output: colorful HTML report -> index.html
"""

import json
import urllib.request
from datetime import datetime, timezone

# ============================================================
# 1. DATA FETCHING (جلب البيانات الحية للبيتكوين والسوق)
# ============================================================
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

# جلب أسعار الأصول الحية (البيتكوين، مؤشر الدولار، العوائد)
btc    = get_price("BTC-USD", 77414.00)
eth    = get_price("ETH-USD",  2650.00)
dxy    = get_price("DX-Y.NYB",  102.15)
y10    = get_price("%5ETNX",      5.018)

# مؤشرات السوق البديلة للبيتكوين
eth_btc_ratio = eth / btc if btc else 0.034
real_yield    = y10 - 3.6

# ============================================================
# 2. DYNAMIC KEY LEVELS (حساب الدعوم والمقاومات ديناميكياً للبيتكوين)
# ============================================================
pivot = round(btc * 0.992, 2)
levels = {
    "R2": round(btc * 1.03, 2),
    "R1": round(btc * 1.015, 2),
    "R0": round(btc * 1.005, 2),
    "Pivot": pivot,
    "S1": round(btc * 0.985, 2),
    "S2": round(btc * 0.97, 2),
    "S3": round(btc * 0.95, 2),
}

# ============================================================
# 3. SENTIMENT SNAPSHOT (معنويات السوق والسيولة)
# ============================================================
sentiment = {
    "crypto_greed_index": 68,
    "market_sentiment": "Greed / Bullish Momentum",
    "trend_strength": 8,
    "bull_probability": 65,
    "bear_probability": 35,
    "institutional_flow": "Strong Inflows",
    "fed_rate": "3.75%-4.00%",
}

# ============================================================
# 4. SCORING ENGINE (منظومة تحليل الصفقات والفرص للبيتكوين)
# ============================================================
def compute_score():
    score = 0
    factors = []

    # تقييم مؤشر الخوف والطمع للكريبتو
    cg = sentiment["crypto_greed_index"]
    if cg > 75:
        score -= 10; factors.append(("Crypto Greed Index", f"{cg}/100", "Extreme Greed — caution for pullback", -10))
    elif cg < 35:
        score += 15; factors.append(("Crypto Greed Index", f"{cg}/100", "Fear zone — contrarian buy opportunity", 15))
    else:
        score += 5;  factors.append(("Crypto Greed Index", f"{cg}/100", "Healthy market momentum", 5))

    # تقييم العائد الحقيقي (Real Yields)
    if real_yield > 2.5:
        score -= 15; factors.append(("Real Yields", f"{real_yield:.2f}%", "High yields — pressure on risk assets", -15))
    else:
        score += 10; factors.append(("Real Yields", f"{real_yield:.2f}%", "Favorable liquidity environment", 10))

    # تقييم السعر مقارنة بنقطة الارتكاز (Pivot)
    if btc > pivot + 50:
        score += 20; factors.append(("Price vs Pivot", f"${btc:,.0f} > ${pivot:,.0f}", "Trading above pivot — strong buyers control", 20))
    elif btc < pivot - 50:
        score -= 20; factors.append(("Price vs Pivot", f"${btc:,.0f} < ${pivot:,.0f}", "Trading below pivot — sellers control", -20))
    else:
        factors.append(("Price vs Pivot", f"At Pivot", "Testing critical pivot zone", 0))

    # تقييم قوة مؤشر الدولار (DXY)
    if dxy > 103:
        score -= 10; factors.append(("DXY Index", f"{dxy:.2f}", "Strong dollar — slight macro headwind", -10))
    else:
        score += 10; factors.append(("DXY Index", f"{dxy:.2f}", "Weak/Neutral dollar — supportive for crypto", 10))

    score = max(-100, min(100, score))

    if score >= 15:      action = "BUY"
    elif score <= -15:   action = "SELL"
    else:                action = "WAIT"

    confidence = min(100, abs(score) + 30)

    if action == "BUY":
        entry, stop, target = levels["S1"], levels["S2"], levels["R1"]
        risk, reward = abs(entry - stop), abs(target - entry)
    elif action == "SELL":
        entry, stop, target = levels["R1"], levels["R2"], levels["S1"]
        risk, reward = abs(stop - entry), abs(entry - target)
    else:
        entry, stop, target = btc, levels["S1"], levels["R1"]
        risk, reward = abs(btc - levels["S1"]), abs(levels["R1"] - btc)

    rr = round(reward / risk, 2) if risk > 0 else 0

    return {"score": score, "action": action, "confidence": confidence,
            "rr": rr, "entry": entry, "stop": stop, "target": target, "factors": factors}

result = compute_score()

# ============================================================
# 5. HTML REPORT (تصميم احترافي مخصص للبيتكوين)
# ============================================================
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

    return f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<title>Bitcoin Institutional Intelligence Report {datetime.now(timezone.utc).strftime('%Y-%m-%d')}</title>
<style>
body{{font-family:'Segoe UI',Arial,sans-serif;background:#0d1117;color:#e6edf3;padding:20px;margin:0}}
.container{{max-width:1000px;margin:auto}}
h1{{color:#f7931a;text-align:center}}
h2{{color:#58a6ff;border-bottom:1px solid #30363d;padding-bottom:6px}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:20px;margin:16px 0}}
.action-box{{text-align:center;padding:24px;border-radius:12px;background:{color}22;border:2px solid {color}}}
.action-label{{font-size:48px;font-weight:bold;color:{color}}}
table{{width:100%;border-collapse:collapse;margin-top:8px}}
th{{text-align:right;color:#8b949e;border-bottom:1px solid #30363d;padding:8px 4px}}
td{{padding:8px 4px;border-bottom:1px solid #21262d}}
.metric{{display:inline-block;margin:8px 16px;text-align:center}}
.val{{font-size:22px;font-weight:bold;color:#f7931a}}
.lbl{{font-size:12px;color:#8b949e}}
.footer{{text-align:center;color:#8b949e;font-size:12px;margin-top:32px}}
</style></head><body><div class="container">
<h1>₿ التقرير الذاتي الآلي لفرص البيتكوين</h1>
<p style="text-align:center;color:#8b949e">{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · Bitcoin Institutional Suite</p>

<div class="card action-box">
  <div class="action-label">{a}</div>
  <p>النتيجة الإجمالية (Score): <b>{result['score']}</b>/100 · مستوى الثقة: <b>{result['confidence']}%</b> · العائد للمخاطرة (R:R): <b>{result['rr']}:1</b></p>
</div>

<div class="card"><h2>📊 نظرة عامة على سوق العملات الرقمية (Market Snapshot)</h2>
<div style="display:flex;flex-wrap:wrap;justify-content:space-around">
  <div class="metric"><div class="val">${btc:,.2f}</div><div class="lbl">سعر البيتكوين (BTC/USD)</div></div>
  <div class="metric"><div class="val">${eth:,.2f}</div><div class="lbl">الإيثريوم (ETH/USD)</div></div>
  <div class="metric"><div class="val">{eth_btc_ratio:.3f}</div><div class="lbl">نسبة ETH/BTC</div></div>
  <div class="metric"><div class="val">{dxy:.2f}</div><div class="lbl">مؤشر الدولار (DXY)</div></div>
  <div class="metric"><div class="val">{real_yield:.2f}%</div><div class="lbl">العائد الحقيقي</div></div>
</div></div>

<div class="card"><h2>🧮 تقييم العوامل والذكاء الاصطناعي (Factor Scorecard)</h2>
<table><tr><th>العامل</th><th>القيمة</th><th>التفسير</th><th>النقاط</th></tr>{factor_rows}</table></div>

<div class="card"><h2>📍 مستويات الدعم والمقاومة الديناميكية (Key Levels)</h2>
<table><tr><th>المستوى الفني</th><th>السعر</th><th>النسبة من السعر الحالي</th></tr>{level_rows}</table></div>

<div class="card"><h2>🧠 معنويات السوق والتدفقات المؤسسية (Sentiment & Flows)</h2>
<table>
<tr><td>مؤشر الخوف والطمع (Crypto Greed)</td><td>{sentiment['crypto_greed_index']} / 100 ({sentiment['market_sentiment']})</td></tr>
<tr><td>قوة الاتجاه العام</td><td>{sentiment['trend_strength']} / 10</td></tr>
<tr><td>احتمالية الصعود / الهبوط</td><td>{sentiment['bull_probability']}% / {sentiment['bear_probability']}%</td></tr>
<tr><td>تدفقات السيولة المؤسسية</td><td>{sentiment['institutional_flow']}</td></tr>
</table></div>

<div class="card"><h2>🎯 خطة التداول الميدانية للبيتكوين (Trade Plan)</h2>
<table>
<tr><td>الاتجاه الموصى به</td><td style="color:{color};font-weight:bold">{a}</td></tr>
<tr><td>منطقة الدخول الموصى بها (Entry)</td><td>${result['entry']:,.2f}</td></tr>
<tr><td>وقف الخسارة الآمن (Stop Loss)</td><td>${result['stop']:,.2f}</td></tr>
<tr><td>الهدف الرئيسي (Take Profit)</td><td>${result['target']:,.2f}</td></tr>
<tr><td>نسبة العائد للمخاطرة (R:R)</td><td>{result['rr']} : 1</td></tr>
</table></div>

<div class="footer">
<p>⚠️ هذا التقرير للأغراض التعليمية والتحليلية فقط ولا يعتبر نصيحة مالية مباشرة.</p>
</div>
</div></body></html>"""

html_content = build_html()
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("=" * 50)
print("✅ BITCOIN REPORT GENERATED SUCCESSFULLY")
print("=" * 50)
print(f"Action     : {result['action']}")
print(f"Score      : {result['score']} / 100")
print(f"Confidence : {result['confidence']}%")
print(f"R:R        : {result['rr']}:1")
print(f"BTC Price  : ${btc:,.2f}")
print("=" * 50)
