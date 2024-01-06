console.log("[Log] Current Player Role: " + currentPlayerRole);
let isUserTurn = true;
let userMoveCompleted = false;
let isMoveExecuted = false;
let pieceId;

async function executeMove(pieceId, currentPosition) {
    let userMove = {
        move: 'USER_MOVE',
        pieceId: pieceId,
        position: currentPosition
    };

    try {
        const response = await fetch('/game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ move: userMove }),
            credentials: 'same-origin',
        });

        // Sprawdź, czy odpowiedź zawiera błąd
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        if (!userMoveCompleted && isUserTurn && userMove.move === 'USER_MOVE') {
            userMoveCompleted = true; // Oznacz, że użytkownik wykonał ruch
            isUserTurn = false; // Ustaw, że teraz jest tura komputera
            executeComputerMove(); // Rozpocznij ruch komputera
        }

    } catch (error) {
        console.error('Error during fetch:', error);
    }
}


function executeComputerMove() {
    const computerMove = {
        move: 'COMPUTER_MOVE',
        position: { row: 0, col: 0 },
        pieceId: pieceId
    };

    let sheepIndex = $(`#${pieceId}`).data('index');

    // Pobierz element wilka, który jest przeciągalny
    const draggableWolf = $("#wolf.ui-draggable");

    // Pobierz wszystkie elementy .sheep, które są przeciągalne
    const draggableSheep = $(".sheep.ui-draggable");

    if (draggableSheep.length > 0) {
        sheepIndex = draggableSheep.attr("id");
    }

    // Sprawdź, czy elementy są już zainicjowane jako przeciągalne
    if (draggableWolf.length > 0) {
        draggableWolf.draggable("enable");
    }
    if (draggableSheep.length > 0) {
        draggableSheep.draggable("enable");
    }

    fetch('/game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ computerMove }),
        credentials: 'same-origin',
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            if (draggableWolf.length > 0) {
                draggableWolf.draggable("disable");
            }

            if (draggableSheep.length > 0) {
                draggableSheep.draggable("disable");
            }
            isUserTurn = true;
            isMoveExecuted = false; // Zresetuj zmienną po zakończeniu tury komputera
            return response.json();
        })
        .then(data => {
            const computerMove = data.chosen_move;  // Odczytaj ruch komputera z danych
            const sheepIndex = data.sheepIndex;

            // Dla każdego pionka owcy, przesuń go zgodnie z ruchem komputera
            moveSheepWithComputerMove(computerMove, sheepIndex);

            // Dla pionka wilka, przesuń go zgodnie z ruchem komputera
            moveWolfWithComputerMove(computerMove);

        })
        .catch(error => {
            console.error('Error during fetch:', error);
        });
}

// Funkcja do przesuwania owiec zgodnie z ruchem komputera
function moveSheepWithComputerMove(computerMove, sheepIndex) {
    const sheepPiece = $("#sheep" + sheepIndex);

    if (sheepPiece && computerMove && computerMove.newPosition) {
        // Zaktualizuj pozycję owcy na planszy
        const newPosition = {
            row: computerMove.newPosition.row,
            col: computerMove.newPosition.col
        };

        sheepPiece.data("current-row", newPosition.row);
        sheepPiece.data("current-col", newPosition.col);
        updatePieceView(sheepPiece, newPosition);
    } else {
        console.error('Invalid computerMove object or newPosition not found:', computerMove);
    }
}

// Funkcja do przesuwania wilka zgodnie z ruchem komputera
function moveWolfWithComputerMove(computerMove) {
    const wolfPiece = $("#wolf");

    if (wolfPiece && computerMove && computerMove.newPosition) {
        // Zaktualizuj pozycję wilka na planszy
        const newPosition = {
            row: computerMove.newPosition.row,
            col: computerMove.newPosition.col
        };

        wolfPiece.data("current-row", newPosition.row);
        wolfPiece.data("current-col", newPosition.col);
        updatePieceView(wolfPiece, newPosition);
    } else {
        console.error('Invalid computerMove object or newPosition not found:', computerMove);
    }
}


// Funkcja inicjalizująca przeciąganie dla owiec
function initializeSheepDraggable() {
    $(".sheep").draggable({
        containment: ".board",
        grid: [50, 50],
        disabled: false,
        drag: function (event, ui) {
            checkCollisions(ui.helper);
            const startPosition = ui.originalPosition;
            const endPosition = ui.position;

            // Sprawdzenie, czy ruch jest na ukos
            if (!isDiagonalMovement(startPosition, endPosition)) {
                // Jeśli nie, przywróć poprzednią pozycję
                $(this).draggable('option', 'revert', true);
            } else {
                // Sprawdzenie, czy pionek nie cofa się do poprzedniego rzędu
                const startRow = Math.floor(startPosition.top / 50);
                const endRow = Math.floor(endPosition.top / 50);
                if (endRow > startRow) {
                    // Jeśli pionek cofa się do poprzedniego rzędu, przywróć poprzednią pozycję
                    $(this).draggable('option', 'revert', true);
                } else {
                    // W przeciwnym razie, usuń opcję revert
                    $(this).draggable('option', 'revert', false);
                }
            }
            },
        stop: function (event, ui) {
            const pieceId = $(this).attr("id");
            const sheepIndex = $(this).data('index');
            handlePieceStop(event, ui, pieceId);
            },
        drop: function (event, ui) {
            const pieceId = $(this).attr("id");
            const sheepIndex = $(this).data('index');
            handlePieceDrop(event, ui, pieceId);
        }
    });
}

function initializeWolfDraggable() {
    $("#wolf").draggable({
        containment: ".board",
        grid: [50, 50],
        disabled: false,
        drag: function (event, ui) {
            checkCollisions(ui.helper);
            const startPosition = ui.originalPosition;
            const endPosition = ui.position;

            // Sprawdzenie, czy ruch jest na ukos
            if (!isDiagonalMovement(startPosition, endPosition)) {
                // Jeśli nie, przywróć poprzednią pozycję
                $(this).draggable('option', 'revert', true);
            } else {
                // W przeciwnym razie, usuń opcję revert
                $(this).draggable('option', 'revert', false);
            }
            },
        stop: function (event, ui) {
            let pieceId = $(this).attr("id");
            handlePieceStop(event, ui, pieceId);
            },
        drop: function (event, ui) {
            const pieceId = $(this).attr("id");
            handlePieceDrop(event, ui, pieceId);
        }
    });
}

// Funkcja do przesyłania ruchu komputera do serwera
function sendComputerMove(computerMove) {
    $.ajax({
        type: "POST",
        contentType: "application/json;charset=utf-8",
        url: "/handle_computer_move",
        data: JSON.stringify({ "computerMove": computerMove }),
        success: function(response) {
            console.log("Odpowiedź serwera:", response);
        },
        error: function(error) {
            console.error("Błąd przy wysyłaniu danych do serwera:", error);
        }
    });
}

function isDiagonalMovement(startPosition, endPosition) {
    const dx = Math.abs(endPosition.left - startPosition.left);
    const dy = Math.abs(endPosition.top - startPosition.top);
    return dx === dy;
}

function handlePieceDrag(event, ui, movePieceFunction) {
    try {
        ui.helper.data("moveReported", false);

        const startPosition = ui.originalPosition;
        const endPosition = ui.helper.position();

        // Sprawdzenie, czy ruch jest na ukos
        if (isDiagonalMovement(startPosition, endPosition)) {
            // Dodaj logikę przemieszczania pionka
            const newPosition = {
                row: Math.floor(endPosition.top / 50),
                col: Math.floor(endPosition.left / 50)
            };

            // Sprawdź kolizje z innymi pionkami
            if (!hasCollisions(ui.helper, newPosition)) {
                // Wykonaj ruch tylko jeśli nie ma kolizji
                movePieceFunction(newPosition);
            } else {
                // Jeśli jest kolizja, przywróć poprzednią pozycję
                ui.helper.css(ui.originalPosition);
            }
        } else {
            // Jeśli ruch nie jest na ukos, przywróć poprzednią pozycję
            ui.helper.css(ui.originalPosition);
        }
    } catch (error) {
        console.error('Error during piece drag:', error);
    }
}

function handlePieceStop(event, ui, pieceId) {
    const currentPosition = {
        row: Math.floor(ui.position.top / 50),
        col: Math.floor(ui.position.left / 50)
    };

    if (!userMoveCompleted && isUserTurn) {
        executeMove(pieceId, currentPosition);
        isMoveExecuted = true;
    }
}

function endUserTurn() {
    $(".piece").draggable("disable"); // Wyłącz przeciąganie dla wszystkich pionków
    isUserTurn = false;
    executeComputerMove();
}

function handlePieceDrop(event, ui, pieceId) {
    if (!isMoveExecuted && isUserTurn) {
        const currentPosition = {
            row: Math.floor(ui.position.top / 50),
            col: Math.floor(ui.position.left / 50)
        };
        if (!hasCollisions(ui.helper, currentPosition)) {
            executeMove(pieceId, currentPosition);
            isMoveExecuted = true;
            endUserTurn();
        } else {
            ui.helper.draggable('option', 'revert', true);
        }
    }
}

function setDraggableProperties() {
    let pieceId = "";

    $(".piece").on("stop", function(event) {
        let ui = event.ui;
        pieceId = $(this).attr("id");

        // Upewnij się, że pieceId nie jest undefined przed wywołaniem startsWith
        if (pieceId) {
            if (currentPlayerRole === "wilk" && pieceId === "wolf") {
                // Wykonaj kod tylko dla wilka
                executeMove(pieceId, {
                    row: Math.floor(ui.position.top / 50),
                    col: Math.floor(ui.position.left / 50)
                });
            } else if (currentPlayerRole === "owca" && pieceId.startsWith("sheep")) {
                // Wykonaj kod tylko dla owiec
                executeMove(pieceId, {
                    row: Math.floor(ui.position.top / 50),
                    col: Math.floor(ui.position.left / 50)
                });
            }
        }
    });

    if (currentPlayerRole === "wilk") {
        pieceId = "wolf";
        initializeWolfDraggable()
    } else if (currentPlayerRole === "owca") {
        pieceId = "sheep";
        initializeSheepDraggable()
    }
}

function checkCollisions(movingPiece) {
    const currentPosition = {
        row: Math.floor(movingPiece.position().top / 50),
        col: Math.floor(movingPiece.position().left / 50)
    };

    if (hasCollisions(movingPiece, currentPosition)) {
                movingPiece.draggable('option', 'revert', true);
    }
}

function hasSheepCollisions(movingPiece, newPosition) {
    const otherSheepPieces = $(".sheep").not(movingPiece);
    let hasCollision = false;

    otherSheepPieces.each(function() {
        const piecePosition = {
            row: Math.floor($(this).position().top / 50),
            col: Math.floor($(this).position().left / 50)
        };

        if (piecePosition.row === newPosition.row && piecePosition.col === newPosition.col) {
            // Znaleziono kolizję
            hasCollision = true;
            return false; // Przerwij pętlę each, ponieważ znaleziono kolizję
        }
    });

    // Sprawdź, czy na nowej pozycji jest już jakaś owca
    const newPositionOccupied = $(".sheep").filter(function() {
        const piecePosition = {
            row: Math.floor($(this).position().top / 50),
            col: Math.floor($(this).position().left / 50)
        };
        return piecePosition.row === newPosition.row && piecePosition.col === newPosition.col;
    }).length > 0;

    return hasCollision || newPositionOccupied;
}



function isCollisionWithWolf(movingPiece, newPosition) {
    const wolfPiece = $("#wolf");
    const wolfPosition = {
        row: Math.floor(wolfPiece.position().top / 50),
        col: Math.floor(wolfPiece.position().left / 50)
    };

    return wolfPosition.row === newPosition.row && wolfPosition.col === newPosition.col;
}


function hasCollisions(movingPiece, newPosition) {
    return isCollisionWithWolf(movingPiece, newPosition) || hasSheepCollisions(movingPiece, newPosition);
}


function isCollision(piece1, piece2) {
    const rect1 = {
        left: piece1.position().left,
        top: piece1.position().top,
        right: piece1.position().left + piece1.width(),
        bottom: piece1.position().top + piece1.height()
    };
    const rect2 = {
        left: piece2.position().left,
        top: piece2.position().top,
        right: piece2.position().left + piece2.width(),
        bottom: piece2.position().top + piece2.height()
    };

    return !(rect1.right < rect2.left ||
        rect1.left > rect2.right ||
        rect1.bottom < rect2.top ||
        rect1.top > rect2.bottom);
}

function moveWolfPiece(currentPosition) {
    const wolfPiece = $("#wolf");
    wolfPiece.data("current-row", currentPosition.row);
    wolfPiece.data("current-col", currentPosition.col);
    updatePieceView(wolfPiece, currentPosition);
}


function moveSheepPiece(currentPosition) {
    const sheepPiece = $(".sheep.ui-draggable-dragging");
    const pieceId = sheepPiece.attr("id");
    sheepPiece.data("current-row", currentPosition.row);
    sheepPiece.data("current-col", currentPosition.col);
    updatePieceView(sheepPiece, currentPosition);
}

function updatePieceView(piece, currentPosition) {
    // Zaktualizuj widok dla danego pionka
    piece.css({
        top: currentPosition.row * 50,
        left: currentPosition.col * 50
    });
}

$(document).ready(function() {
    setDraggableProperties();
});
