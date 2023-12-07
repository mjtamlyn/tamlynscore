function sum(array) {
    return array.reduce((a, b) => {
        if (a === 'M') {
            a = 0;
        }
        if (b === 'M') {
            b = 0;
        }
        return a + b;
    }, 0);
}

function currentEnd(score) {
    if (!score.arrows.length) {
        return 1;
    }
    return Math.floor((score.arrows.length - 1) / score.endLength) + 1;
};

function getEnd(score, endNumber) {
    return score.arrows.slice((endNumber - 1) * score.endLength, endNumber * score.endLength);
}

function isEndComplete(score, endNumber) {
    return getEnd(score, endNumber).length == score.endLength;
}

function getRunningTotal(score, endNumber) {
    if (!endNumber) {
        return sum(score.arrows);
    }
    return sum(score.arrows.slice(0, endNumber * score.endLength));
}

function getArrowsShot(score) {
    return score.arrows.length;
}

function getEndScore(score, endNumber) {
    return sum(getEnd(score, endNumber));
}

function getGoldCount(score, endNumber) {
    let arrows = score.arrows;
    if (endNumber) {
        arrows = getEnd(score, endNumber);
    }
    return sum(arrows.map(a => ((a === 10) ? 1 : 0)));
}


export { currentEnd, getEnd, isEndComplete, getEndScore, getRunningTotal, getGoldCount, getArrowsShot };
