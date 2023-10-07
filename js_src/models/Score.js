const sum = (array) => array.reduce((a, b) => a + b, 0);

class Score {
    constructor({ target, name, categories, arrows, endLength = 3 }) {
        this.target = target;
        this.name = name;
        this.categories = categories;
        this.arrows = arrows;
        this.endLength = endLength;
    }

    getEnd(endNumber) {
        return this.arrows.slice((endNumber - 1) * this.endLength, endNumber * this.endLength);
    }

    getEndScore(endNumber) {
        return sum(this.getEnd(endNumber));
    }

    getRunningTotal(endNumber) {
        return sum(this.arrows.slice(0, endNumber * this.endLength));
    }

    setScore(endNumber, cursorPosition, number) {
        this.arrows[(endNumber - 1) * this.endLength + cursorPosition] = number;
    }
}

export default Score;
