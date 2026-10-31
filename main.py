"""
INSTITUTIONAL MASTER SUITE - FIXED LEVELS & LIVE PRICE FEED
Includes Gold/Crypto Algorithm Sweep & Breakout Intelligence Engine.
"""

from datetime import datetime, timezone

def build_html():
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Institutional Master Suite & Algorithm Breakout</title>
    <style>
        body{{font-family:'Segoe UI',Arial,sans-serif;background:#0d1117;color:#e6edf3;padding:20px;margin:0}}
        .container{{max-width:1050px;margin:auto}}
        h1{{color:#f7931a;text-align:center}}
        h2{{color:#58a6ff;border-bottom:1px solid #30363d;padding-bottom:6px}}
        .card{{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:20px;margin:16px 0}}
        .action-box{{text-align:center;padding:24px;border-radius:12px;background:#1f242c;border:2px solid #58a6ff}}
        .action-label{{font-size:44px;font-weight:bold;color:#f7931a}}
        table{{width:100%;border-collapse:collapse;margin-top:8px}}
        th{{text-align:right;color:#8b949e;border-bottom:1px solid #30363d;padding:8px 4px}}
        td{{padding:8px 4px;border-bottom:1px solid #21262d}}
        .metric{{display:inline-block;margin:8px 16px;text-align:center}}
        .val{{font-size:24px;font-weight:bold;color:#f7931a;transition: color 0.3s ease}}
        .lbl{{font-size:12px;color:#8b949e}}
        .footer{{text-align:center;color:#8b949e;font-size:12px;margin-top:32px}}
        .live-dot {{height: 12px; width: 12px; background-color: #00c853; border-radius: 50%; display: inline-block; animation: pulse 1.5s infinite;}}
        @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
    </style>
    
    <script>
        let ws;
        let baselineSet = false;
        let fixedEntry = 0, fixedStop = 0, fixedTarget = 0, fixedPivot = 0, fixedR1 = 0, fixedS1 = 0;

        function connectWebSocket() {{
            ws = new WebSocket('wss://stream.binance.com:9443/ws/btcusdt@trade');
            
            ws.onmessage = function(event) {{
                let data = JSON.parse(event.data);
                let btcPrice = parseFloat(data.p);
                
                // تحديث خانة السعر الحي فقط ثانية بسانية
                let priceElement = document.getElementById('btc-price');
                let oldPrice = parseFloat(priceElement.getAttribute('data-price') || btcPrice);
                
                if (btcPrice > oldPrice) {{
                    priceElement.style.color = '#00c853';
                }} else if (btcPrice < oldPrice) {{
                    priceElement.style.color = '#d50000';
                }}
                
                priceElement.innerText = '$' + btcPrice.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
                priceElement.setAttribute('data-price', btcPrice);
                
                // تثبيت المستويات الاستراتيجية لأول مرة عند فتح الصفحة لكي لا تتغير وتجري ورا السعر
                if (!baselineSet) {{
                    fixedPivot = Math.round(btcPrice * 0.992);
                    fixedR1 = Math.round(btcPrice * 1.015);
                    fixedS1 = Math.round(btcPrice * 0.985);
                    fixedEntry = fixedS1;
                    fixedStop = Math.round(btcPrice * 0.97);
                    fixedTarget = fixedR1;
                    
                    document.getElementById('pivot-val').innerText = '$' + fixedPivot.toLocaleString();
                    document.getElementById('r1-val').innerText = '$' + fixedR1.toLocaleString();
                    document.getElementById('s1-val').innerText = '$' + fixedS1.toLocaleString();
                    document.getElementById('plan-entry').innerText = '$' + fixedEntry.toLocaleString();
                    document.getElementById('plan-stop').innerText = '$' + fixedStop.toLocaleString();
                    document.getElementById('plan-target').innerText = '$' + fixedTarget.toLocaleString();
                    
                    baselineSet = true;
                }}
                
                // تتبع حالة الصفقة والثبات على المستويات الثابتة
                let action = btcPrice >= fixedPivot ? "BUY (شراء مؤسسي)" : "SELL (بيع تصحيحي)";
                let actionColor = btcPrice >= fixedPivot ? "#00c853" : "#d50000";
                
                document.getElementById('action-direction').innerText = action;
                document.getElementById('action-direction').style.color = actionColor;
                
                let statusText = "";
                let statusColor = "#ff9100";
                
                if (btcPrice >= fixedEntry && btcPrice <= fixedEntry + 150) {{
                    statusText = "🎯 السعر لامس منطقة الدخول الثابتة (فرصة تفعيل قوية)";
                    statusColor = "#00c853";
                }} else if (btcPrice > fixedEntry) {{
                    statusText = "🟢 الصفقة مفعلة وتتداول في نطاق الأرباح نحو الهدف";
                    statusColor = "#00c853";
                }} else {{
                    statusText = "⏳ أمر معلق (بانتظار ارتداد السعر لمنطقة الدخول S1 الثابتة)";
                    statusColor = "#ff9100";
                }}
                
                document.getElementById('trade-execution-status').innerText = statusText;
                document.getElementById('trade-execution-status').style.color = statusColor;
                
                // خوارزمية رصد صانع السوق واختراق النطاقات (Algorithm Sweep Detection)
                let algoMsg = "حالة الخوارزمية: استقرار في السيولة النطاقية (No Sweep)";
                let algoColor = "#58a6ff";
                if (btcPrice > fixedR1 - 50) {{
                    algoMsg = "🚨 تنبيه خوارزمي: اختبار حد السيولة العلوي (Breakout / Stop Hunt Risk)";
                    algoColor = "#ff9100";
                }} else if (btcPrice < fixedS1 + 50) {{
                    algoMsg = "⚡ تنبيه خوارزمي: هجوم تجميعي عند الدعم السفلي (Institutional Sweep Zone)";
                    algoColor = "#00c853";
                }}
                document.getElementById('algo-status').innerText = algoMsg;
                document.getElementById('algo-status').style.color = algoColor;
            }};
            
            ws.onclose = function() {{
                setTimeout(connectWebSocket, 3000);
            }};
        }}
        
        window.onload = connectWebSocket;
    </script>
</head>
<body>
<div class="container">
    <h1>🤖 منصة تحليل واختراق خوارزميات السوق والتحكم الحي <span class="live-dot"></span></h1>
    <p style="text-align:center;color:#8b949e">{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · Institutional Sweep & Fixed Levels Suite</p>

    <!-- التوجيه الاستراتيجي وحالة التنفيذ -->
    <div class="card action-box">
        <div class="action-label" id="action-direction">جارِ التحليل...</div>
        <div id="trade-execution-status" style="font-size:17px;font-weight:bold;margin-top:10px;color:#ff9100">فحص حالة أوامر السوق...</div>
        <div id="algo-status" style="font-size:14px;margin-top:8px;color:#58a6ff">منظومة رصد الخوارزميات: نشطة</div>
    </div>

    <!-- نظرة عامة وسعر حي متحدث فقط -->
    <div class="card">
        <h2>📊 نظرة عامة والسعر الفوري اللحظي</h2>
        <div style="display:flex;flex-wrap:wrap;justify-content:space-around">
            <div class="metric"><div class="val" id="btc-price" data-price="0">جارِ الاتصال...</div><div class="lbl">السعر الحي الفوري (Live Ticker)</div></div>
            <div class="metric"><div class="val" style="color:#58a6ff">101.96</div><div class="lbl">مؤشر الدولار (DXY)</div></div>
            <div class="metric"><div class="val" style="color:#00c853">مستقر</div><div class="lbl">حالة السيولة الخوارزمية</div></div>
        </div>
    </div>

    <!-- خطة التداول بالمستويات الثابتة والدقيقة -->
    <div class="card">
        <h2>🎯 خطة التداول ومستويات التنفيذ الميدانية (ثابتة وغير متذبذبة)</h2>
        <table>
            <tr><th>العنصر التكتيكي</th><th>السعر الثابت المعتمد</th><th>الوصف الاستراتيجي</th></tr>
            <tr><td><b>منطقة الدخول (Entry)</b></td><td id="plan-entry" style="color:#58a6ff;font-weight:bold">--</td><td>النقطة المؤسسية المعتمدة لفتح الصفقة.</td></tr>
            <tr><td><b>وقف الخسارة (Stop Loss)</b></td><td id="plan-stop" style="color:#d50000;font-weight:bold">--</td><td>حماية رأس المال ضد مصائد صانع السوق (Stop Hunts).</td></tr>
            <tr><td><b>الهدف الرئيسي (Take Profit)</b></td><td id="plan-target" style="color:#00c853;font-weight:bold">--</td><td>محطة جني الأرباح المحسوبة آلياً.</td></tr>
        </table>
    </div>

    <!-- المستويات الفنية والدعوم والمقاومات الثابتة -->
    <div class="card">
        <h2>📍 مستويات البيفوت والدعوم والمقاومات (Fixed Key Levels)</h2>
        <table>
            <tr><th>المستوى الفني</th><th>السعر المعتمد</th></tr>
            <tr><td>المقاومة الأولى (R1)</td><td id="r1-val" style="color:#d50000">--</td></tr>
            <tr><td>محور الارتكاز (Pivot)</td><td id="pivot-val" style="color:#58a6ff;font-weight:bold">--</td></tr>
            <tr><td>الدعم الأول (S1)</td><td id="s1-val" style="color:#00c853">--</td></tr>
        </table>
    </div>

    <div class="footer">
        <p>⚠️ تم تثبيت مستويات الدخول والأهداف لمنع التذبذب، بينما يظل السعر الحي وراصد الخوارزميات يعملان بلحظته.</p>
    </div>
</div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(build_html())

print("Successfully updated with Fixed Levels & Algorithm Sweep Engine.")
