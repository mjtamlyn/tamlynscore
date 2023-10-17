const sum = (array) => array.reduce((a, b) => {
    if (a === 'M') {
        a = 0;
    }
    if (b === 'M') {
        b = 0;
    }
    return a + b;
}, 0);

const compareArrows = (a, b) => {
    if (a === 'M') {
        a = 0;
    }
    if (b === 'M') {
        b = 0;
    }
    if (a < b) {
        return 1;
    } else if (a > b) {
        return -1;
    }
    return 0;
};

const isDescending = (end) => {
    const sorted = end.toSorted(compareArrows);
    if (end.length !== sorted.length) {
        return false;
    }
    for (let i=0; i<end.length; i++) {
        if (end[i] !== sorted[i]) {
            return false;
        }
    }
    return true
}

class Score {
    constructor({ target, name, categories, arrows = [], endLength = 3 }) {
        this.target = target;
        this.name = name;
        this.categories = categories;
        this.arrows = arrows;
        this.endLength = endLength;
    }

    currentEnd() {
        if (!this.arrows.length) {
            return 1;
        }
        return Math.floor((this.arrows.length - 1) / this.endLength) + 1;
    }

    getEnd(endNumber) {
        return this.arrows.slice((endNumber - 1) * this.endLength, endNumber * this.endLength);
    }

    isEndComplete(endNumber) {
        return this.getEnd(endNumber).length == this.endLength;
    }

    getEndScore(endNumber) {
        return sum(this.getEnd(endNumber));
    }

    getArrowsShot() {
        return this.arrows.length;
    }

    getRunningTotal(endNumber) {
        if (!endNumber) {
            return sum(this.arrows);
        }
        return sum(this.arrows.slice(0, endNumber * this.endLength));
    }

    getGoldCount() {
        return sum(this.arrows.map(a => ((a === 10) ? 1 : 0)));
    }

    setScore(endNumber, cursorPosition, number) {
        let arrowNumber = (endNumber - 1) * this.endLength + cursorPosition;
        if (this.arrows.length < arrowNumber) {
            arrowNumber = this.arrows.length;
        }
        this.arrows[arrowNumber] = number;
        const end = this.getEnd(endNumber);
        if (!isDescending(end)) {
            this.arrows.splice((endNumber - 1) * this.endLength, this.endLength, ...end.toSorted(compareArrows));
        };
    }
}

export default Score;
