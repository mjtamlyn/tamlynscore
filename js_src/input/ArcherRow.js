import React from 'react';

import { getEnd, getEndScore, getRunningTotal } from './utils';
import ArcherRowDetails from './ArcherRowDetails';


const InputBox = ({ onClick, value = '\u00A0', active = false }) => {
    let className = 'archers__score__input';
    if (active) {
        className += ' archers__score__input--active';
    };
    return (
        <div onClick={ onClick } className={ className }>{ value }</div>
    );
};


const ArcherRow = ({ score, endNumber, active, cursorPosition = null, setPosition }) => {
    const currentArrows = getEnd(score, endNumber);
    const endLength = score.round.endLength;

    const boxes = [...Array(endLength).keys()].map((index) => {
        return (
            <InputBox onClick={ setPosition(score, index) } active={ active && cursorPosition === index } value={ currentArrows[index] } />
        );
    });

    return (
        <div className={ active ? 'archers__row archers__row--current' : 'archers__row' }>
            <ArcherRowDetails score={ score } />
            <div className="archers__score" style={ { 'gridTemplateColumns': `repeat(${endLength + 2}, 1fr)` } }>
                { boxes }
                <div className="archers__score__total">{ getEndScore(score, endNumber) }</div>
                <div className="archers__score__total">{ getRunningTotal(score, endNumber) }</div>
            </div>
        </div>
    )
};

export default ArcherRow;
