import React from 'react';

import ArcherRowDetails from './ArcherRowDetails';


const ArcherRowSummary = ({ score }) => {
    return (
        <div className="archers__row archers__row--summary">
            <ArcherRowDetails score={ score } />
            <div className="archers__summary">
                <div className="archers__summary__total">
                    { score.getRunningTotal() } <small className="archers__summary__legend">total</small>
                </div>
                <div className="archers__summary__golds">
                    { score.getGoldCount() } <small className="archers__summary__legend">10s</small>
                </div>
                <div className="archers__summary__arrows-shot">
                    { score.getArrowsShot() } / 30 <small className="archers__summary__legend">arrows shot</small>
                </div>
            </div>
        </div>
    );
};

export default ArcherRowSummary;
