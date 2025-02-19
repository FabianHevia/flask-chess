document.addEventListener('DOMContentLoaded', () => {
    console.log("Iniciando juego...");
    
    // Verificar que las librerías estén cargadas
    if (typeof Chess === 'undefined') {
        console.error("Chess.js no está cargado");
        return;
    }
    
    if (typeof Chessboard === 'undefined') {
        console.error("Chessboard.js no está cargado");
        return;
    }

    let board = null;
    let game = new Chess();
    let playerTimer = timeLimit;
    let botTimer = timeLimit;
    let playerInterval = null;
    let botInterval = null;
    let isPlayerTurn = true;

    function onSnapEnd() {
        // Esta función se llama después de que una pieza es soltada
        // Asegura que el tablero refleje la posición actual del juego
        board.position(game.fen());
    }

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
        return true;
    }

    function makeMove(move) {
        let moveResult;
        
        // Si el movimiento viene como string (del bot), convertirlo a objeto
        if (typeof move === 'string') {
            moveResult = game.move({
                from: move.substring(0, 2),
                to: move.substring(2, 4),
                promotion: move.length === 5 ? move.substring(4, 5) : undefined
            });
        } else {
            moveResult = game.move(move);
        }
        
        if (moveResult === null) return false;
        
        // Animación más suave
        board.position(game.fen(), true);
        
        if (game.game_over()) {
            clearInterval(playerInterval);
            clearInterval(botInterval);
            if (game.in_checkmate()) {
                alert(isPlayerTurn ? '¡Jaque mate! Has ganado.' : '¡Jaque mate! Has perdido.');
            } else if (game.in_draw()) {
                alert('¡Tablas!');
            }
            return true;
        }
        
        isPlayerTurn = !isPlayerTurn;
        if (playerInterval) clearInterval(playerInterval);
        if (botInterval) clearInterval(botInterval);
        startTimer();
        
        if (!isPlayerTurn) {
            // "Pensando" indicador
            const statusEl = document.createElement('div');
            statusEl.className = 'thinking-status';
            statusEl.textContent = `${botName} está pensando...`;
            document.querySelector('.game-info').appendChild(statusEl);
            
            // Turno del bot con delay aleatorio mínimo
            setTimeout(() => {
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
                .then(response => response.json())
                .then(data => {
                    // Remover el indicador de "pensando"
                    statusEl.remove();
                    makeMove(data.move);
                })
                .catch(error => {
                    console.error("Error getting bot move:", error);
                    statusEl.remove();
                    isPlayerTurn = true;
                });
            }, 500); // Delay mínimo para la interfaz
        }
        
        return true;
    }

    function onDrop(source, target) {
        const move = {
            from: source,
            to: target,
            promotion: 'q'
        };
        
        if (!makeMove(move)) {
            return 'snapback';
        }
    }

    // Inicializar el tablero
    board = Chessboard('board', {
        position: 'start',
        draggable: true,
        pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png',
        onDragStart: onDragStart,
        onDrop: onDrop,
        onSnapEnd: onSnapEnd
    });

    console.log("Tablero inicializado:", board);
    
    // Redimensionar el tablero cuando cambie el tamaño de la ventana
    window.addEventListener('resize', () => board.resize());

    // Iniciar temporizadores
    startTimer();
});