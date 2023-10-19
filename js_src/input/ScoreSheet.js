import React from 'react';

import ArcherRowDetails from './ArcherRowDetails';


const ScoreSheet = ({ score, toSummary }) => {
    const ends = [...Array(20).keys()];
    const scoreRows = ends.map((endNumber) => {
        const end = score.getEnd(endNumber + 1);
        return (
            <div className="archers__score" key={ endNumber }>
                <div>{ end[0] || '-' }</div>
                <div>{ end[1] || '-' }</div>
                <div>{ end[2] || '-' }</div>
                <div className="archers__score__total">{ score.getEndScore(endNumber + 1) }</div>
                <div className="archers__score__running">{ score.getRunningTotal(endNumber + 1) }</div>
            </div>
        );
    });
    return (
        <>
            <div className="full-height-page__card">
                <div className="archers">
                    <div className="archers__row">
                        <ArcherRowDetails score={ score } />
                        { scoreRows }
                    </div>
                    <div className="archers__summary">
                        <div className="archers__summary__total">
                            { score.getRunningTotal() } <small className="archers__summary__legend">total</small>
                        </div>
                        <div className="archers__summary__golds">
                            { score.getGoldCount() } <small className="archers__summary__legend">10s</small>
                        </div>
                        <div className="archers__summary__arrows-shot">
                            { score.getArrowsShot() } / 60 <small className="archers__summary__legend">arrows shot</small>
                        </div>
                    </div>
                </div>
            </div>
            <div className="actions">
                <a className="actions__button" onClick={ toSummary }>Back</a>
            </div>
        </>
    );
};

export default ScoreSheet;
