import React from 'react';


const ScoreInput = () => {
    return (
        <div className="input">
            <div className="input__control input__control--gold">10</div>
            <div className="input__control input__control--gold">9</div>
            <div className="input__control input__control--red">8</div>
            <div className="input__control input__control--red">7</div>
            <div className="input__control input__control--blue">6</div>
            <div className="input__control input__control--blue">5</div>
            <div className="input__control input__control--black">4</div>
            <div className="input__control input__control--black">3</div>
            <div className="input__control input__control--white">2</div>
            <div className="input__control input__control--white">1</div>
            <div className="input__control input__control--green input__control--miss">M</div>
        </div>
    );
};

export default ScoreInput;
