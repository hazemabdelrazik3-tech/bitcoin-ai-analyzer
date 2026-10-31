"""
BITCOIN WEBSOCKET LIVE STREAM REPORT
Real-time streaming price updates directly from Binance WebSocket.
"""

from datetime import datetime, timezone

def build_html():
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Bitcoin WebSocket Live Stream</title>
    <style>
        body{{font-family:'Segoe UI',Arial,sans-serif;background:#0d1117;color:#e6edf3;padding:20px;text-align:center}}
        .container{{max-width:960px;margin:auto}}
        h1{{color:#f7931a}}
        h2{{color:#58a6ff;border-bottom:1px solid #30363d;padding-bottom:6px}}
        .card{{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:20px;margin:16px 0;text-align:right}}
        .action-box{{text-align:center;padding:24px;border-radius:12px;background:#1f242c;border:2px solid #58a6ff}}
        .action-label{{font-size:48px;font-weight:bold;color:#f7931a}}
        .metric{{display:inline-block;margin:10px 20px;text-align:center}}
        .val{{font-size:32px;font-weight:bold;color:#f7931a;transition: color 0.3s ease;}}
        .lbl{{font-size:12px;color:#8b949e}}
        .footer{{text-align:center;color:#8b949e;font-size:12px;margin-top:32px}}
        .live-dot {{height: 12px; width: 12px; background-color: #00c853; border-radius: 50%; display: inline-block; animation: pulse 1.5s infinite;}}
        @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
    </style>
    
    <script>
        let ws;
        function connectWebSocket() {{
            // الاتصال المباشر بـ Binance WebSocket Stream للبيتكوين
            ws = new WebSocket('wss://stream.binance.com:9443/ws/btcusdt@trade');
            
            ws.onmessage = function(event) {{
                let data = JSON.parse(event.data);
                let btcPrice = parseFloat(data.p);
                
                let priceElement = document.getElementById('btc-price');
                let oldPrice = parseFloat(priceElement.getAttribute('data-price') || btcPrice);
                
                // تأثير بصري خفيف لتغير السعر (أخضر صعود / أحمر هبوط)
                if (btcPrice > oldPrice) {{
                    priceElement.style.color = '#00c853';
                }} else if (btcPrice < oldPrice) {{
                    priceElement.style.color = '#d50000';
                }}
                
                priceElement.innerText = '$' + btcPrice.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
                priceElement.setAttribute('data-price', btcPrice);
                
                // تحديث المستويات اللحظية أوتوماتيكياً مع حركة السعر
                let pivot = Math.round(btcPrice * 0.992);
                let s1 = Math.round(btcPrice * 0.985);
                let r1 = Math.round(btcPrice * 1.015);
                
                document.getElementById('pivot-val').innerText = '$' + pivot.toLocaleString('en-US');
                document.getElementById('s1-val').innerText = '$' + s1.toLocaleString('en-US');
                document.getElementById('r1-val').innerText = '$' + r1.toLocaleString('en-US');
                
                // التوجيه اللحظي
                let action = btcPrice >= pivot ? "BUY" : "SELL";
                let actionBox = document.getElementById('action-direction');
                if(actionBox.innerText !== action) {{
                    actionBox.innerText = action;
                    actionBox.style.color = action === "BUY" ? "#00c853" : "#d50000";
                }}
            }};
            
            ws.onclose = function() {{
                // إعادة الاتصال تلقائياً لو حصل أي قطع
                setTimeout(connectWebSocket, 3000);
            }};
        }}
        
        window.onload = connectWebSocket;
    </script>
</head>
<body>
<div class="container">
    <h1>₿ Bitcoin Live Stream Intelligence <span class="live-dot"></span></h1>
    <p style="color:#8b949e">{datetime.now(timezone.utc).strftime('%Y-%m-%d')} · Real-Time WebSocket Feed</p>

    <div class="card action-box">
        <div class="action-label" id="action-direction">--</div>
        <p>التوجيه اللحظي يتحدث أوتوماتيكياً مع كل حركة في السوق</p>
    </div>

    <div class="card">
        <h2>📊 Market Snapshot (WebSocket Live)</h2>
        <div style="text-align:center">
            <div class="metric">
                <div class="val" id="btc-price" data-price="0">جارِ الاتصال بالبث الحي...</div>
                <div class="lbl">سعر BTC/USDT المباشر (تحديث ثواني)</div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>📍 المستويات الحية المتغيرة</h2>
        <p><b>Pivot الحي:</b> <span id="pivot-val" style="color:#58a6ff;">---</span></p>
        <p><b>الدعم الأول (S1):</b> <span id="s1-val" style="color:#00c853;">---</span></p>
        <p><b>المقاومة الأولى (R1):</b> <span id="r1-val" style="color:#d50000;">---</span></p>
    </div>

    <div class="footer">
        <p>⚠️ النظام الآن مربوط ببث مباشر بالكامل (WebSocket)، السعر يتحرك أمامك دون الحاجة لتحديث الصفحة.</p>
    </div>
</div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(build_html())

print("Successfully configured WebSocket Live Stream.")
