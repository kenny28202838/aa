
from flask import Flask, request, jsonify, Response, render_template_string
import requests
import os
import cv2

app = Flask(__name__)

# 讀取 LINE Token
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')

# ✅ LINE Bot 警報 API
@app.route('/alert', methods=['POST'])
def send_alert():
    data = request.get_json()
    user_id = data.get('user_id')
    message = data.get('message')

    if not user_id or not message:
        return jsonify({'status': 'error', 'message': '缺少 user_id 或 message'}), 400

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }

    try:
        response = requests.post(
            'https://api.line.me/v2/bot/message/push',
            headers=headers,
            json=payload
        )
        print("LINE 回應：", response.status_code, response.text)
        if response.status_code == 200:
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'line_response': response.text}), response.status_code
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ✅ webhook（顯示 userId）
@app.route('/webhook', methods=['POST'])
def webhook():
    body = request.get_json()
    print("Webhook Event:", body)

    try:
        events = body.get("events", [])
        for event in events:
            if event.get("type") == "message":
                user_id = event["source"]["userId"]
                reply_token = event["replyToken"]
                print(f"使用者 userId：{user_id}")
                reply_payload = {
                    "replyToken": reply_token,
                    "messages": [{"type": "text", "text": f"你的 userId 是：{user_id}"}]
                }
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
                }
                requests.post(
                    "https://api.line.me/v2/bot/message/reply",
                    headers=headers,
                    json=reply_payload
                )
    except Exception as e:
        print("Webhook 錯誤：", e)

    return "OK", 200

# ✅ 直播頁面 HTML
LIVE_HTML = '''
<!doctype html>
<title>即時影像直播</title>
<h2 style="text-align:center;">📡 即時監視畫面</h2>
<div style="text-align:center;">
  <img src="/video_feed" width="640" height="360">
</div>
'''

# RTSP 串流網址（請改為你自己的）
RTSP_URL = "rtsp://kenny1231256:kenny28202838@192.168.0.101:554/stream1"

@app.route('/live')
def live_page():
    return render_template_string(LIVE_HTML)

def generate_frames():
    cap = cv2.VideoCapture(RTSP_URL)
    while True:
        success, frame = cap.read()
        if not success:
            continue
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# ✅ 啟動 Flask 應用
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
