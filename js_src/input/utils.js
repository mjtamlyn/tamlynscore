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

function getEnd(score, endNumber, endLength) {
    return score.arrows.slice((endNumber - 1) * (endLength || score.endLength), endNumber * (endLength || score.endLength));
}

function isEndComplete(score, endNumber) {
    return getEnd(score, endNumber).length == score.endLength;
}

function getRunningTotal(score, endNumber, endLength) {
    if (!endNumber) {
        return sum(score.arrows);
    }
    return sum(score.arrows.slice(0, endNumber * (endLength || score.endLength)));
}

function getArrowsShot(score) {
    return score.arrows.length;
}

function getEndScore(score, endNumber, endLength) {
    return sum(getEnd(score, endNumber, endLength));
}

function getGoldCount(score, endNumber, endLength) {
    let arrows = score.arrows;
    if (endNumber) {
        arrows = getEnd(score, endNumber, endLength);
    }
    return sum(arrows.map(a => ((a === 10) ? 1 : 0)));
}


export { currentEnd, getEnd, isEndComplete, getEndScore, getRunningTotal, getGoldCount, getArrowsShot };
