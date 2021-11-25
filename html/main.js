function updateMoves(game, movebox) {
  let s = "";
  let i = 2;
  for (const move of game.history()) {
    if (i % 2 == 0) {
      s += i/2 + ". ";
    }
    s += move + " ";
    i++;
  }
  movebox.innerHTML = s
}

window.addEventListener("DOMContentLoaded", () => {
  const root = document.getElementById("boards");
  const websocket = new WebSocket("ws://localhost:8000");
  var boards = {};

  websocket.addEventListener("message", ({ data }) => {
    const event = JSON.parse(data);
    let game = new Chess();
    game.load_pgn(event.pgn);

    let element = null;
    if (!(Object.keys(boards).includes(event.game))) {
      element = document.createElement('div');
      element.id = event.game;
      element.classList.add("board");
      root.appendChild(element);

      title = document.createElement('h2');
      title.innerHTML = event.game;
      element.appendChild(title);

      board_div = document.createElement('div');
      board_div.classList.add("position");
      element.appendChild(board_div);

      moves_div = document.createElement('div');
      moves_div.classList.add("moves");
      element.appendChild(moves_div);

      let board = new Chessboard(board_div, {
        position: 'start',
        pieceTheme: "lib/img/chesspieces/wikipedia/{piece}.png",
      });

      boards[event.game] = { board: board, moves: moves_div };
    }
    boards[event.game].board.position(game.fen());
    updateMoves(game, boards[event.game].moves);
  })
});
