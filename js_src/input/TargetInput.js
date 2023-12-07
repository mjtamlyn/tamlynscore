import React, { useState, useContext } from 'react';

import { InputScoresDispatchContext } from '../context/InputScoresContext';

import { isEndComplete, getEnd } from './utils';
import ArcherRow from './ArcherRow';
import ScoreInput from './ScoreInput';


const TargetInput = ({ scores, endNumber, toSummary }) => {
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
        if (cursorPosition + 1 === activeScore.endLength) {
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
            { (cursorPosition !== null ) && <ScoreInput setArrow={ setArrow } /> }
            <div className="actions">
                <div className="actions__button" onClick={ toSummary }>
                    Save
                </div>
            </div>
        </>
    );
};

export default TargetInput;
