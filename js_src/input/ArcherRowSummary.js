import React from 'react';

import ArcherRowDetails from './ArcherRowDetails';
import { getRunningTotal, getGoldCount, getArrowsShot } from './utils';


const ArcherRowSummary = ({ score, showScoreSheet }) => {
    return (
        <div className="archers__row archers__row--summary">
            <ArcherRowDetails score={ score } />
            <div className="archers__summary">
                <div className="archers__summary__total">
                    { getRunningTotal(score) } <small className="archers__summary__legend">total</small>
                </div>
                <div className="archers__summary__golds">
                    { getGoldCount(score) } <small className="archers__summary__legend">10s</small>
                </div>
                <div className="archers__summary__arrows-shot">
                    { getArrowsShot(score) } / { score.round.totalArrows } <small className="archers__summary__legend">arrows shot</small>
                </div>
                <a className="btn btn-small score-sheet" onClick={ () => showScoreSheet(score) }>Scores</a>
            </div>
        </div>
    );
};

export default ArcherRowSummary;
