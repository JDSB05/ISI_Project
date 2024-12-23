import os
import telepot
from telepot.loop import MessageLoop
from flask import Flask, request, jsonify

# Flask initialization
app = Flask(__name__)

# Telegram bot token
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
if not bot_token:
    raise ValueError("You must set the TELEGRAM_BOT_TOKEN environment variable with your Telegram bot token.")
bot = telepot.Bot(bot_token)

# Dictionary to store the association between chat_ids and car_ids
user_car_ids = {}

def handle_telegram_messages(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(f"\n[INFO] Message received from Telegram: {msg}")
    if content_type == 'text':
        text = msg['text']
        if text.startswith('/start'):
            # User starts the bot and provides car_id and sensor_id
            parts = text.split()
            if len(parts) == 3:
                car_id = parts[1]
                sensor_id = parts[2]
                user_car_ids[chat_id] = (car_id, sensor_id)
                bot.sendMessage(chat_id, f'Welcome! You will receive alerts from car {car_id} and sensor {sensor_id}.')
                print(f"[INFO] User {chat_id} associated with car {car_id} and sensor {sensor_id}.")
            else:
                bot.sendMessage(chat_id, 'Please use the command /start <car_id> <sensor_id> to start.')
        elif text == '/stop':
            if chat_id in user_car_ids:
                del user_car_ids[chat_id]
            bot.sendMessage(chat_id, 'You will no longer receive alerts.')
            print(f"[INFO] User {chat_id} stopped the bot.")
        else:
            bot.sendMessage(chat_id, 'Command not recognized. Use /start <car_id> <sensor_id> or /stop.')

def send_telegram_message(car_id, sensor_id, message):
    print(f"\n[INFO] Preparing to send message to car {car_id} and sensor {sensor_id}: {message}")
    # Send message to all users associated with car_id and sensor_id
    for chat_id, (user_car_id, user_sensor_id) in user_car_ids.items():
        if user_car_id == car_id and user_sensor_id == sensor_id:
            print(f"[INFO] Sending message to chat_id {chat_id}")
            bot.sendMessage(chat_id, message)

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    car_id = data.get('car_id')
    sensor_id = data.get('sensor_id')
    message = data.get('message')
    if car_id and sensor_id and message:
        send_telegram_message(car_id, sensor_id, message)
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

if __name__ == '__main__':
    print("[INFO] Starting Telegram bot...")
    MessageLoop(bot, handle_telegram_messages).run_as_thread()
    print("[INFO] Telegram bot started and waiting for messages...")
    app.run(host='0.0.0.0', port=5001)