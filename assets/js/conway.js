const CELL_SIZE = 10
const BOARD_WIDTH = document.documentElement.offsetWidth
const BOARD_HEIGHT = document.documentElement.offsetHeight

const CELL_COLOR = "rgb(0, 64, 0)"
const BOARD_COLOR = "rgb(0, 0, 0)"

class Board {
    #cellSize = CELL_SIZE
    #backgroundColor = BOARD_COLOR

    constructor(canvas) {
        this.canvas = canvas
        this.ctx = this.canvas.getContext("2d")
    }

    drawBackground() {
        const { width, height } = this.canvas

        this.ctx.fillStyle = this.#backgroundColor
        this.ctx.fillRect(0, 0, width, height)
    }

    get size() {
        const { width, height } = this.canvas

        return {
            cellNumberX: Math.ceil(width / this.#cellSize),
            cellNumberY: Math.ceil(height / this.#cellSize),
            cellSize: this.#cellSize,
        }
    }

    get context() {
        return this.ctx
    }
}

class Cell {
    #alive = true
    #neighbors = 0

    constructor(ctx, x, y, cellSize) {
        this.ctx = ctx

        this.x = x
        this.y = y
        this.cellSize = cellSize
    }

    nextGeneration() {
        if (!this.#alive && this.#neighbors === 3) {
            this.#alive = true
        } else {
            this.#alive = this.#alive && (this.#neighbors === 2 || this.#neighbors === 3)
        }
    }

    draw() {
        if (this.#alive) {
            this.ctx.fillStyle = CELL_COLOR
            this.ctx.fillRect(...this.#position)
        }
    }

    get #position() {
        return [
            this.x * this.cellSize,
            this.y * this.cellSize,
            this.cellSize,
            this.cellSize
        ]
    }

    set alive(alive) {
        this.#alive = alive
    }

    get alive() {
        return this.#alive
    }

    set neighbors(neighbors) {
        this.#neighbors = neighbors
    }
}


class Game {
    #cells = []

    constructor(canvas) {
        this.canvas = canvas
        this.board = new Board(this.canvas)

        this.canvas.width = BOARD_WIDTH
        this.canvas.height = BOARD_HEIGHT
    }

    initialize = () => {
        this.initializeCells()
        this.launch()
    }

    initializeCells() {
        for (let i = 0; i < this.board.size.cellNumberX; i++) {
            this.#cells[i] = []

            for (let j = 0; j < this.board.size.cellNumberY; j++) {
                this.#cells[i][j] = new Cell(this.board.context, i, j, this.board.size.cellSize)
                this.#cells[i][j].alive = Math.random() > 0.8
                this.#cells[i][j].draw()
            }
        }
    }

    launch = () => {
        this.board.drawBackground()

        this.updateCells()

        requestAnimationFrame(this.launch)
    }

    updateCells = () => {
        for (let i = 0; i < this.board.size.cellNumberX; i++) {
            for (let j = 0; j < this.board.size.cellNumberY; j++) {
                this.updateCellNeighbors(i, j);
            }
        }

        for (let i = 0; i < this.board.size.cellNumberX; i++) {
            for (let j = 0; j < this.board.size.cellNumberY; j++) {
                this.#cells[i][j].nextGeneration()
                this.#cells[i][j].draw()
            }
        }
    }

    updateCellNeighbors = (x, y) => {
        let aliveNeighborsCount = 0

        const neighborCoords = [
            [x, y + 1],
            [x, y - 1],
            [x + 1, y],
            [x - 1, y],
            [x + 1, y + 1],
            [x - 1, y - 1],
            [x + 1, y - 1],
            [x - 1, y + 1]
        ]

        for (const coords of neighborCoords) {
            let [xCord, yCord] = coords;

            const xOutOfBounds = xCord < 0 || xCord >= this.board.size.cellNumberX
            const yOutOfBounds = yCord < 0 || yCord >= this.board.size.cellNumberY

            const wrappedX = xOutOfBounds ? (xCord + this.board.size.cellNumberX) % this.board.size.cellNumberX : xCord
            const wrappedY = yOutOfBounds ? (yCord + this.board.size.cellNumberY) % this.board.size.cellNumberY : yCord

            if (this.#cells[wrappedX]?.[wrappedY]?.alive) {
                aliveNeighborsCount++
            }
        }

        this.#cells[x][y].neighbors = aliveNeighborsCount
    }
}

const canvas = document.getElementById("game-board")
// canvas.style.width = '100%';
// canvas.style.height = '100%';
// canvas.width = canvas.offsetWidth;
// canvas.height = canvas.offsetHeight;
const game = new Game(canvas)

game.initialize()

// canvas.height = canvas.width / (canvas.clientWidth / canvas.clientHeight);
