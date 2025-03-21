import React from 'react';


const ScoreInput = ({ setArrow, hasXs = false, gold9s = false, hasElevens = false }) => {
    const clickHandler = (value) => {
        return (e) => {
            e.preventDefault();
            setArrow(value);
        };
    };
    let className = 'score-input';
    if (hasXs) {
        className += ' score-input--has-xs';
    }
    if (hasElevens) {
        className += ' score-input--has-elevens';
    }
    if (gold9s) {
        className += ' score-input--gold-9s';
    }

    return (
        <div className={ className }>
            { !gold9s && hasXs && <div onClick={ clickHandler('X') } className="score-input__control score-input__control--gold score-input__control--small">X</div> }
            { !gold9s && hasElevens && <div onClick={ clickHandler(11) } className="score-input__control score-input__control--gold score-input__control--small">11</div> }
            { !gold9s && !hasElevens && !hasXs && <div onClick={ clickHandler(10) } className="score-input__control score-input__control--gold">10</div> }
            <div onClick={ clickHandler(9) } className="score-input__control score-input__control--gold">9</div>
            { !gold9s && <div onClick={ clickHandler(8) } className="score-input__control score-input__control--red">8</div> }
            <div onClick={ clickHandler(7) } className="score-input__control score-input__control--red">7</div>
            { !gold9s && hasXs && <div onClick={ clickHandler(10) } className="score-input__control score-input__control--gold score-input__control--small">10</div> }
            { !gold9s && hasElevens && <div onClick={ clickHandler(10) } className="score-input__control score-input__control--gold score-input__control--small">10</div> }
            { !gold9s && <div onClick={ clickHandler(6) } className="score-input__control score-input__control--blue">6</div> }
            <div onClick={ clickHandler(5) } className="score-input__control score-input__control--blue">5</div>
            { !gold9s && <div onClick={ clickHandler(4) } className="score-input__control score-input__control--black">4</div> }
            <div onClick={ clickHandler(3) } className="score-input__control score-input__control--black">3</div>
            { !gold9s && <div onClick={ clickHandler(2) } className="score-input__control score-input__control--white">2</div> }
            <div onClick={ clickHandler(1) } className="score-input__control score-input__control--white">1</div>
            <div onClick={ clickHandler('M') } className="score-input__control score-input__control--green score-input__control--miss">M</div>
        </div>
    );
};

export default ScoreInput;
