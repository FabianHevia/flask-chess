from flask import Flask, render_template, jsonify, request
from config import GAME_MODES
from bots import load_bots
import chess
import time

app = Flask(__name__)
app.config.from_object('config')

BOTS = load_bots()

@app.route('/')
def index():
    return render_template('index.html', bots=BOTS, modes=GAME_MODES)

@app.route('/game/<bot_name>/<mode>')
def game(bot_name, mode):
    if bot_name not in BOTS or mode not in GAME_MODES:
        return "Invalid parameters", 400
    return render_template('game.html', 
                         bot=BOTS[bot_name], 
                         mode=mode, 
                         modes=GAME_MODES)

@app.route('/move', methods=['POST'])
def make_move():
    data = request.json
    print("Received data:", data)  # Debug log
    
    board = chess.Board(data['fen'])
    bot_name = data['bot']
    print(f"Bot name: {bot_name}")  # Debug log
    
    bot = BOTS[bot_name]
    print(f"Using bot: {bot.name}")  # Debug log
    
    # Obtener el movimiento del bot
    bot_move = bot.get_move(board)
    print(f"Bot move: {bot_move}")  # Debug log
    
    # Hacer el movimiento en el tablero
    board.push(bot_move)
    
    return jsonify({
        'move': bot_move.uci(),
        'fen': board.fen()
    })

if __name__ == '__main__':
    app.run(debug=True)