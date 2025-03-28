function sum(array) {
    return array.reduce((a, b) => {
        if (a === 'M') {
            a = 0;
        }
        if (b === 'M') {
            b = 0;
        }
        if (a === 'X') {
            a = 10;
        }
        if (b === 'X') {
            b = 10;
        }
        return a + b;
    }, 0);
}

function currentEnd(score) {
    if (!score.arrows.length) {
        return 1;
    }
    return Math.floor((score.arrows.length - 1) / score.round.endLength) + 1;
};

function getEnd(score, endNumber, endLength) {
    return score.arrows.slice((endNumber - 1) * (endLength || score.round.endLength), endNumber * (endLength || score.round.endLength));
}

function isEndComplete(score, endNumber) {
    return getEnd(score, endNumber).length == score.round.endLength;
}

function getRunningTotal(score, endNumber, endLength) {
    if (!endNumber) {
        return sum(score.arrows);
    }
    return sum(score.arrows.slice(0, endNumber * (endLength || score.round.endLength)));
}

function getArrowsShot(score) {
    return score.arrows.length;
}

function getEndScore(score, endNumber, endLength) {
    return sum(getEnd(score, endNumber, endLength));
}

function getHitCount(score, endNumber, endLength) {
    let arrows = score.arrows;
    if (endNumber) {
        arrows = getEnd(score, endNumber, endLength);
    }
    return sum(arrows.map(a => ((a && a !== 'M') ? 1 : 0)));
}

function getGoldCount(score, endNumber, endLength) {
    let arrows = score.arrows;
    if (endNumber) {
        arrows = getEnd(score, endNumber, endLength);
    }
    if (score.round.resultsOptions.gold9s) {
        return sum(arrows.map(a => (a === 9) ? 1 : 0));
    }
    return sum(arrows.map(a => ((a === 10 || a === 'X') ? 1 : 0)));
}

function getGoldLabel(score) {
    if (score.round.resultsOptions.gold9s) {
        return '9s';
    }
    return '10s';
}

function getXCount(score, endNumber, endLength) {
    let arrows = score.arrows;
    if (endNumber) {
        arrows = getEnd(score, endNumber, endLength);
    }
    return sum(arrows.map(a => ((a && a === 'X') ? 1 : 0)));
}

function getElevenCount(score, endNumber, endLength) {
    let arrows = score.arrows;
    if (endNumber) {
        arrows = getEnd(score, endNumber, endLength);
    }
    return sum(arrows.map(a => ((a && a === 11) ? 1 : 0)));
}



export { currentEnd, getEnd, isEndComplete, getEndScore, getRunningTotal, getGoldCount, getGoldLabel, getHitCount, getXCount, getElevenCount, getArrowsShot };
