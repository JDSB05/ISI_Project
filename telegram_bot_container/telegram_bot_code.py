import os
import telepot
from telepot.loop import MessageLoop
from flask import Flask, request, jsonify

# Inicialização do Flask
app = Flask(__name__)

# Token do bot Telegram
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
if not bot_token:
    raise ValueError("Você deve definir a variável de ambiente TELEGRAM_BOT_TOKEN com o token do seu bot Telegram.")
bot = telepot.Bot(bot_token)

# Dicionário para armazenar a associação entre chat_ids e car_ids
user_car_ids = {}

def handle_telegram_messages(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(f"Mensagem recebida do Telegram: {msg}")
    if content_type == 'text':
        text = msg['text']
        if text.startswith('/start'):
            # Usuário inicia o bot e fornece o car_id
            parts = text.split()
            if len(parts) == 2:
                car_id = parts[1]
                user_car_ids[chat_id] = car_id
                bot.sendMessage(chat_id, f'Bem-vindo! Você receberá alertas do carro {car_id}.')
                print(f"Usuário {chat_id} associado ao carro {car_id}.")
            else:
                bot.sendMessage(chat_id, 'Por favor, use o comando /start <car_id> para iniciar.')
        elif text == '/stop':
            if chat_id in user_car_ids:
                del user_car_ids[chat_id]
            bot.sendMessage(chat_id, 'Você não receberá mais alertas.')
            print(f"Usuário {chat_id} parou o bot.")
        else:
            bot.sendMessage(chat_id, 'Comando não reconhecido. Use /start <car_id> ou /stop.')

def send_telegram_message(car_id, message):
    print(f"Preparando para enviar mensagem para o carro {car_id}: {message}")
    # Enviar mensagem para todos os usuários associados ao car_id
    for chat_id, user_car_id in user_car_ids.items():
        if user_car_id == car_id:
            print(f"Enviando mensagem para o chat_id {chat_id}")
            bot.sendMessage(chat_id, message)

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    car_id = data.get('car_id')
    message = data.get('message')
    if car_id and message:
        send_telegram_message(car_id, message)
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'error', 'message': 'Dados inválidos'}), 400

if __name__ == '__main__':
    print("Iniciando bot Telegram...")
    MessageLoop(bot, handle_telegram_messages).run_as_thread()
    print("Bot Telegram iniciado e aguardando mensagens...")
    app.run(host='0.0.0.0', port=5001)