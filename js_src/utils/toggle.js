import React from 'react';

const Toggle = ({ on, setOn }) => {
    var className = "toggle";
    if (on) {
        className += " toggle--on"
    } else {
        className += " toggle--off"
    }
    return <div className={ className } onClick={ e => setOn(!on) } />;
};

export default Toggle;
