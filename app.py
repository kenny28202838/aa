from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 將你的 Channel Access Token 放這裡
LINE_CHANNEL_ACCESS_TOKEN = 'LINE_CHANNEL_ACCESS_TOKEN'

@app.route('/alert', methods=['POST'])
def send_alert():
    data = request.get_json()
    user_id = data.get('user_id')  # 使用者 LINE ID
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

    response = requests.post(
        'https://api.line.me/v2/bot/message/push',
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'response': response.text}), 500

if __name__ == '__main__':
    app.run(debug=True)