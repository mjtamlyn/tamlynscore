import React from 'react';

import { getEnd, getEndScore, getRunningTotal } from './utils';
import ArcherRowDetails from './ArcherRowDetails';


const ArcherRow = ({ score, endNumber, active, cursorPosition = null, setPosition }) => {
    const currentArrows = getEnd(score, endNumber);

    let inputCls1 = 'archers__score__input';
    let inputCls2 = 'archers__score__input';
    let inputCls3 = 'archers__score__input';

    if (active) {
        if (cursorPosition === 0) {
            inputCls1 += ' archers__score__input--active';
        } else if (cursorPosition === 1) {
            inputCls2 += ' archers__score__input--active';
        } else if (cursorPosition === 2) {
            inputCls3 += ' archers__score__input--active';
        }
    }

    return (
        <div className={ active ? 'archers__row archers__row--current' : 'archers__row' }>
            <ArcherRowDetails score={ score } />
            <div className="archers__score">
                <div onClick={ setPosition(score, 0) } className={ inputCls1 }>{ currentArrows[0] || '\u00A0' }</div>
                <div onClick={ setPosition(score, 1) } className={ inputCls2 }>{ currentArrows[1] }</div>
                <div onClick={ setPosition(score, 2) } className={ inputCls3 }>{ currentArrows[2] }</div>
                <div className="archers__score__total">{ getEndScore(score, endNumber) }</div>
                <div className="archers__score__total">{ getRunningTotal(score, endNumber) }</div>
            </div>
        </div>
    )
};

export default ArcherRow;
