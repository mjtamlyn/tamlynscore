import React, { createContext, useEffect } from 'react';
import { useImmerReducer } from 'use-immer';

import { getEnd } from '../input/utils';
import useActionQueue from '../utils/useActionQueue';

const InputScoresContext = createContext(null);
const InputScoresDispatchContext = createContext(null);


function compareArrows(a, b) {
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

function isDescending(end) {
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

const inputScoresReducer = (scores, action) => {
    const actionQueue = scores.actionQueue;

    switch (action.type) {
        case 'setScore': {
            const score = scores.scores.find(s => s.target === action.score.target);
            let arrowNumber = (action.endNumber - 1) * score.round.endLength + action.cursorPosition;
            if (score.arrows.length < arrowNumber) {
                arrowNumber = score.arrows.length;
            }
            score.arrows[arrowNumber] = action.number;
            const end = getEnd(score, action.endNumber);
            if (!isDescending(end)) {
                const startNum = (action.endNumber - 1) * score.round.endLength;
                const endNum = startNum + score.round.endLength;
                score.arrows.splice(startNum, score.round.endLength, ...end.toSorted(compareArrows));
                for (let i=startNum; i<endNum; i++) {
                    actionQueue.doAction({ type: 'SETARROW', params: {score: score.id, arrowOfRound: i + 1, arrowValue: score.arrows[i] }});
                }
            } else {
                actionQueue.doAction({ type: 'SETARROW', params: {score: score.id, arrowOfRound: arrowNumber + 1, arrowValue: action.number }});
            };
            return;
        }
        default: {
            throw Error('TargetListContext: Unknown action: ' + action.type);
        }
    }
};

const InputScoresProvider = ({ children, api, round, scores: initialScores }) => {
    const initialState = {
        scores: initialScores.map(score => { return { round, ...score } }),
        actionQueue: useActionQueue(api),
    };
    const [scores, dispatch] = useImmerReducer(inputScoresReducer, initialState);

    return (
        <InputScoresContext.Provider value={ scores }>
            <InputScoresDispatchContext.Provider value={ dispatch }>
                { children }
            </InputScoresDispatchContext.Provider>
        </InputScoresContext.Provider>
    );
};

export { InputScoresContext, InputScoresDispatchContext, InputScoresProvider };
