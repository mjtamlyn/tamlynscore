import React, { useState } from 'react';

import Score from '../models/Score';

import ArcherRow from './ArcherRow';
import EventHeader from './EventHeader';
import ScoreInput from './ScoreInput';


const scoreA = new Score({
    target: '1A',
    name: 'Nicola Wood',
    categories: {
        bowstyle: 'Compound',
        gender: 'Women',
    },
    arrows: [10, 9, 9, 10, 10, 9, 10, 9, 8],
});
const scoreB = new Score({
    target: '1B',
    name: 'Antony Wood',
    categories: {
        bowstyle: 'Recurve',
        gender: 'Men',
    },
    arrows: [10, 9, 9, 10, 10, 9, 10],
});
const scoreC = new Score({
    target: '1C',
    name: 'Hannah Brown',
    categories: {
        bowstyle: 'Compound',
        gender: 'Women',
    },
    arrows: [10, 10, 9, 10, 10, 9],
});
const scoreD = new Score({
    target: '1D',
    name: 'Steve Mitchell',
    categories: {
        bowstyle: 'Compound',
        gender: 'Men',
    },
    arrows: [10, 9, 9, 10, 10, 9],
});
const scores = [scoreA, scoreB, scoreC, scoreD];

const TargetInput = () => {
    const endLength = 3;
    const [endNumber, setEndNumber] = useState(3);
    const [cursorPosition, setCursorPosition] = useState(1);
    const [activeScore, setActiveScore] = useState(scoreB);

    const setArrow = (number) => {
        return (e) => {
            activeScore.setScore(endNumber, cursorPosition, number);
            if (cursorPosition + 1 === endLength) {
                setCursorPosition(0);
                const currentIndex = scores.indexOf(activeScore);
                if (currentIndex + 1 < scores.length) {
                    setActiveScore(scores[currentIndex + 1]);
                } else {
                    setActiveScore(scores[0]);
                    setEndNumber(endNumber + 1);
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
        <div className="full-height-page">
            <EventHeader round="WA 18" endNumber={ endNumber } />
            <div className="archers">
                <ArcherRow score={ scoreA } endNumber={ endNumber } active={ activeScore === scoreA } cursorPosition={ cursorPosition } setPosition={ setPosition } />
                <ArcherRow score={ scoreB } endNumber={ endNumber } active={ activeScore === scoreB } cursorPosition={ cursorPosition } setPosition={ setPosition } />
                <ArcherRow score={ scoreC } endNumber={ endNumber } active={ activeScore === scoreC } cursorPosition={ cursorPosition } setPosition={ setPosition } />
                <ArcherRow score={ scoreD } endNumber={ endNumber } active={ activeScore === scoreD } cursorPosition={ cursorPosition } setPosition={ setPosition } />
            </div>
            <ScoreInput setArrow={ setArrow } />
        </div>
    );
};

export default TargetInput;
