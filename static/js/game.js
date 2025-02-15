let board = null;
let game = new Chess();
let playerTimer = timeLimit;
let botTimer = timeLimit;
let playerInterval = null;
let botInterval = null;
let isPlayerTurn = true;

function updateTimer(time) {
    const minutes = Math.floor(time / 60);
    const seconds = time % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function startTimer() {
    document.getElementById('player-timer').textContent = updateTimer(playerTimer);
    document.getElementById('bot-timer').textContent = updateTimer(botTimer);
    
    if (isPlayerTurn) {
        if (playerInterval) clearInterval(playerInterval);
        playerInterval = setInterval(() => {
            playerTimer--;
            document.getElementById('player-timer').textContent = updateTimer(playerTimer);
            if (playerTimer <= 0) {
                clearInterval(playerInterval);
                alert('¡Tiempo agotado! Has perdido.');
                game.reset();
                board.position(game.fen());
            }
        }, 1000);
    } else {
        if (botInterval) clearInterval(botInterval);
        botInterval = setInterval(() => {
            botTimer--;
            document.getElementById('bot-timer').textContent = updateTimer(botTimer);
            if (botTimer <= 0) {
                clearInterval(botInterval);
                alert('¡Tiempo agotado! Has ganado.');
                game.reset();
                board.position(game.fen());
            }
        }, 1000);
    }
}

function onDragStart(source, piece) {
    if (game.game_over()) return false;
    if (!isPlayerTurn) return false;
    if (piece.search(/^b/) !== -1) return false;
}

function makeMove(move) {
    game.move(move);
    board.position(game.fen());
    
    if (game.game_over()) {
        clearInterval(playerInterval);
        clearInterval(botInterval);
        if (game.in_checkmate()) {
            alert(isPlayerTurn ? '¡Jaque mate! Has perdido.' : '¡Jaque mate! Has ganado.');
        } else if (game.in_draw()) {
            alert('¡Tablas!');
        }
        return;
    }
    
    isPlayerTurn = !isPlayerTurn;
    if (playerInterval) clearInterval(playerInterval);
    if (botInterval) clearInterval(botInterval);
    startTimer();
    
    if (!isPlayerTurn) {
        // Turno del bot
        setTimeout(() => {
            console.log("Requesting bot move with FEN:", game.fen());
            console.log("Bot name:", botName.toLowerCase());
            
            fetch('/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fen: game.fen(),
                    bot: botName.toLowerCase()
                })
            })
            .then(response => {
                console.log("Bot response:", response);
                return response.json();
            })
            .then(data => {
                console.log("Bot move data:", data);
                makeMove(data.move);
            })
            .catch(error => {
                console.error("Error getting bot move:", error);
            });
        }, 500);
    }
}

function onDrop(source, target) {
    const move = game.move({
        from: source,
        to: target,
        promotion: 'q'
    });
    
    if (move === null) return 'snapback';
    makeMove(move);
}

board = Chessboard('board', {
    position: 'start',
    draggable: true,
    onDragStart: onDragStart,
    onDrop: onDrop
});

// Iniciar temporizadores
startTimer();

document.getElementById('resign').addEventListener('click', () => {
    if (confirm('¿Estás seguro de que quieres abandonar la partida?')) {
        clearInterval(playerInterval);
        clearInterval(botInterval);
        alert('Has abandonado la partida.');
        game.reset();
        board.position(game.fen());
    }
});

document.getElementById('draw').addEventListener('click', () => {
    if (confirm('¿Quieres ofrecer tablas?')) {
        // Simulamos una respuesta del bot basada en la posición actual
        const evaluation = Math.random(); // En una implementación real, esto vendría del bot
        if (evaluation > 0.7) { // 30% de probabilidad de aceptar tablas
            clearInterval(playerInterval);
            clearInterval(botInterval);
            alert('El bot ha aceptado las tablas. Partida finalizada.');
            game.reset();
            board.position(game.fen());
        } else {
            alert('El bot ha rechazado tu oferta de tablas. La partida continúa.');
        }
    }
});

// Manejar el redimensionamiento de la ventana
window.addEventListener('resize', () => {
    board.resize();
});

// Prevenir el cierre accidental de la ventana durante una partida
window.addEventListener('beforeunload', (e) => {
    if (!game.game_over()) {
        e.preventDefault();
        e.returnValue = '¿Estás seguro de que quieres abandonar la partida?';
    }
});

// Función para reiniciar el juego
function resetGame() {
    clearInterval(playerInterval);
    clearInterval(botInterval);
    game.reset();
    board.position('start');
    playerTimer = timeLimit;
    botTimer = timeLimit;
    isPlayerTurn = true;
    startTimer();
}

// Teclas de acceso rápido
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'z') { // Ctrl+Z para deshacer
        game.undo();
        game.undo(); // Deshacer tanto el movimiento del jugador como el del bot
        board.position(game.fen());
    } else if (e.key === 'Escape') { // Escape para abrir menú de abandono
        document.getElementById('resign').click();
    }
});