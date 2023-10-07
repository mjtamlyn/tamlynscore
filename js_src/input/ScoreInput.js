import React from 'react';


const ScoreInput = ({ setArrow }) => {
    return (
        <div className="input">
            <div onClick={ setArrow(10) } className="input__control input__control--gold">10</div>
            <div onClick={ setArrow(9) } className="input__control input__control--gold">9</div>
            <div onClick={ setArrow(8) } className="input__control input__control--red">8</div>
            <div onClick={ setArrow(7) } className="input__control input__control--red">7</div>
            <div onClick={ setArrow(6) } className="input__control input__control--blue">6</div>
            <div onClick={ setArrow(5) } className="input__control input__control--blue">5</div>
            <div onClick={ setArrow(4) } className="input__control input__control--black">4</div>
            <div onClick={ setArrow(3) } className="input__control input__control--black">3</div>
            <div onClick={ setArrow(2) } className="input__control input__control--white">2</div>
            <div onClick={ setArrow(1) } className="input__control input__control--white">1</div>
            <div onClick={ setArrow('M') } className="input__control input__control--green input__control--miss">M</div>
        </div>
    );
};

export default ScoreInput;
