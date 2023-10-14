import React, { useState } from 'react';

import ArcherRow from './ArcherRow';
import ScoreInput from './ScoreInput';


const TargetInput = ({ scores, endNumber, toSummary }) => {
    const endLength = 3;
    const [scoreA, scoreB, scoreC, scoreD] = scores;

    let initialActive = null;
    let initialCursor = 0;

    scores.forEach((score) => {
        if (!score.isEndComplete(endNumber) && !initialActive) {
            initialActive = score;
            initialCursor = score.getEnd(endNumber).length;
        }
    });

    const [cursorPosition, setCursorPosition] = useState(initialCursor);
    const [activeScore, setActiveScore] = useState(initialActive);

    const setArrow = (number) => {
        return (e) => {
            activeScore.setScore(endNumber, cursorPosition, number);
            if (cursorPosition + 1 === endLength) {
                setCursorPosition(0);
                const currentIndex = scores.indexOf(activeScore);
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
    }

    const setPosition = (score, position) => {
        return (e) => {
            setActiveScore(score);
            setCursorPosition(position);
        }
    }

    return (
        <>
            <div className="archers">
                <ArcherRow score={ scoreA } endNumber={ endNumber } active={ activeScore === scoreA } cursorPosition={ cursorPosition } setPosition={ setPosition } />
                <ArcherRow score={ scoreB } endNumber={ endNumber } active={ activeScore === scoreB } cursorPosition={ cursorPosition } setPosition={ setPosition } />
                <ArcherRow score={ scoreC } endNumber={ endNumber } active={ activeScore === scoreC } cursorPosition={ cursorPosition } setPosition={ setPosition } />
                <ArcherRow score={ scoreD } endNumber={ endNumber } active={ activeScore === scoreD } cursorPosition={ cursorPosition } setPosition={ setPosition } />
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
