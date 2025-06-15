from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('61Az0wfM526mnrQN2kabye473Ey3R8/8Y6TYJ2K5EiQt4roZDTWHnACGOCx/7oKOua7zIK4vHUuNOjFzaB9km2 LPSRTvHfYN744JvU/jwuuWsoVHTNh8rXfhXEAJZCmVGq4uoUJJGUaTLKeM7h5FPQdB04t89/1O/w1cDnyilFU=')

@app.route('/webhook', methods=['POST'])
def webhook():
    body = request.get_json()
    print("Webhook Event:", body)  # ✅ 你可以從這裡看 userId

    # 自動回傳文字訊息（測試用）
    try:
        events = body.get("events", [])
        for event in events:
            if event.get("type") == "message":
                user_id = event["source"]["userId"]
                reply_token = event["replyToken"]
                message_text = event["message"]["text"]

                # 把 userId 打印出來
                print(f"使用者 userId：{user_id}")

                # 回傳訊息給使用者（確認 webhook 有效）
                reply_payload = {
                    "replyToken": reply_token,
                    "messages": [{
                        "type": "text",
                        "text": f"你的 userId 是：{user_id}"
                    }]
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
        print("處理 webhook 發生錯誤：", e)

    return "OK", 200


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
        "messages": [
            {"type": "text", "text": message}
        ]
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
        print("Exception:", e)
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
