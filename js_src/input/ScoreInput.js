import React from 'react';


const ScoreInput = ({ setArrow }) => {
    const clickHandler = (value) => {
        return (e) => {
            e.preventDefault();
            setArrow(value);
        };
    };
    return (
        <div className="score-input">
            <div onClick={ clickHandler(10) } className="score-input__control score-input__control--gold">10</div>
            <div onClick={ clickHandler(9) } className="score-input__control score-input__control--gold">9</div>
            <div onClick={ clickHandler(8) } className="score-input__control score-input__control--red">8</div>
            <div onClick={ clickHandler(7) } className="score-input__control score-input__control--red">7</div>
            <div onClick={ clickHandler(6) } className="score-input__control score-input__control--blue">6</div>
            <div onClick={ clickHandler(5) } className="score-input__control score-input__control--blue">5</div>
            <div onClick={ clickHandler(4) } className="score-input__control score-input__control--black">4</div>
            <div onClick={ clickHandler(3) } className="score-input__control score-input__control--black">3</div>
            <div onClick={ clickHandler(2) } className="score-input__control score-input__control--white">2</div>
            <div onClick={ clickHandler(1) } className="score-input__control score-input__control--white">1</div>
            <div onClick={ clickHandler('M') } className="score-input__control score-input__control--green score-input__control--miss">M</div>
        </div>
    );
};

export default ScoreInput;
