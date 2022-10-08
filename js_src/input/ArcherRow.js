import React from 'react';


const ArcherRow = () => {
    return (
        <div className="archers__row">
            <div className="archers__target">1A</div>
            <div className="archers__name">Nicola Wood</div>
            <div className="archers__categories">
                <span className="pill bowstyle compound">Compound</span>
                &nbsp;
                <span className="pill gender women">Women</span>
            </div>
            <div className="archers__score">
                <div className="archers__score__input">10</div>
                <div className="archers__score__input">9</div>
                <div className="archers__score__input">9</div>
                <div className="archers__score__total">
                    28
                </div>
                <div className="archers__score__running">
                    83
                </div>
            </div>
        </div>
    )
};

export default ArcherRow;
