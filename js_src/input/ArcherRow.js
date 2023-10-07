import React from 'react';


const ArcherRow = ({ score, endNumber, active, cursorPosition = null, setPosition }) => {
    const currentArrows = score.getEnd(endNumber);

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
            <div className="archers__target">{ score.target }</div>
            <div className="archers__name">{ score.name }</div>
            <div className="archers__categories">
                <span className={ 'pill bowstyle ' + score.categories.bowstyle.toLowerCase() }>{ score.categories.bowstyle }</span>
                &nbsp;
                <span className={ 'pill gender ' + score.categories.gender.toLowerCase() }>{ score.categories.gender }</span>
            </div>
            <div className="archers__score">
                <div onClick={ setPosition(score, 0) } className={ inputCls1 }>{ currentArrows[0] || '\u00A0' }</div>
                <div onClick={ setPosition(score, 1) } className={ inputCls2 }>{ currentArrows[1] }</div>
                <div onClick={ setPosition(score, 2) } className={ inputCls3 }>{ currentArrows[2] }</div>
                <div className="archers__score__total">{ score.getEndScore(endNumber) }</div>
                <div className="archers__score__running">{ score.getRunningTotal(endNumber) }</div>
            </div>
        </div>
    )
};

export default ArcherRow;
