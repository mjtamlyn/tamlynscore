import React, { useState, useContext } from 'react';

import { InputScoresDispatchContext, InputScoresQueueContext } from '../context/InputScoresContext';
import ErrorState from '../utils/ErrorState';

import { isEndComplete, getEnd } from './utils';
import ArcherRow from './ArcherRow';
import ScoreInput from './ScoreInput';


const TargetInput = ({ scores, round, endNumber, toSummary }) => {
    const actionQueue = useContext(InputScoresQueueContext);
    const dispatch = useContext(InputScoresDispatchContext);

    let initialActive = null;
    let initialCursor = null;

    scores.forEach((score) => {
        if (!isEndComplete(score, endNumber) && !initialActive) {
            initialActive = score;
            initialCursor = getEnd(score, endNumber).length;
        } else {
        }
    });

    const [cursorPosition, setCursorPosition] = useState(initialCursor);
    const [activeScore, setActiveScore] = useState(initialActive);

    const setArrow = (number) => {
        dispatch({ type: 'setScore', score: activeScore, endNumber, cursorPosition, number });
        if (cursorPosition + 1 === activeScore.round.endLength) {
            setCursorPosition(0);
            const currentIndex = scores.findIndex(s => s.target === activeScore.target);
            if (currentIndex + 1 < scores.length) {
                setActiveScore(scores[currentIndex + 1]);
            } else {
                setCursorPosition(null);
                setActiveScore(null);
            }
        } else {
            setCursorPosition(cursorPosition + 1);
        }
    }

    const setPosition = (score, position) => {
        return (e) => {
            setActiveScore(score);
            setCursorPosition(position);
        }
    }

    const scoresRendered = scores.map(score => <ArcherRow score={ score } endNumber={ endNumber } active={ activeScore && (score.target === activeScore.target) } cursorPosition={ cursorPosition } setPosition = { setPosition } key={ score.target } /> );

    return (
        <>
            <div className="archers">
                { scoresRendered }
            </div>
            { (cursorPosition !== null ) && <ScoreInput setArrow={ setArrow } hasXs={ round.resultsOptions.hasXs } gold9s={ round.resultsOptions.gold9s } /> }
            <div className="actions">
                <div className="actions__button" onClick={ toSummary }>
                    Save
                </div>
            </div>
            <div className="sync-status">{ actionQueue.status }</div>
            { actionQueue.status === 'error' && <ErrorState error={ actionQueue.error } /> }
        </>
    );
};

export default TargetInput;
