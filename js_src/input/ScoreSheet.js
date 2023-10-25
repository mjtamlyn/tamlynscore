import React from 'react';

import ArcherRowDetails from './ArcherRowDetails';


const ScoreSheet = ({ score, toSummary }) => {
    const ends = [...Array(20).keys()];
    const scoreRows = ends.map((endNumber) => {
        const end = score.getEnd(endNumber + 1);
        return (
            <>
                <div>{ end[0] || '-' }</div>
                <div>{ end[1] || '-' }</div>
                <div>{ end[2] || '-' }</div>
                <div className="archers__score__total">{ score.getEndScore(endNumber + 1) }</div>
                <div className="archers__score__total">{ score.getGoldCount(endNumber + 1) }</div>
                <div className="archers__score__total">{ score.getRunningTotal(endNumber + 1) }</div>
            </>
        );
    });
    return (
        <>
            <div className="full-height-page__card">
                <div className="archers__row">
                    <ArcherRowDetails score={ score } />
                    <div className="archers__score" style={ { gridTemplateColumns: 'repeat(6, 1fr)'} }>
                        <div className="archers__score__heading archers__score__heading--span">Arrows</div>
                        <div className="archers__score__heading">S</div>
                        <div className="archers__score__heading">10s</div>
                        <div className="archers__score__heading">RT</div>
                        { scoreRows }
                        <div style={ { gridColumnEnd: 'span 3' } } />
                        <div className="archers__score__grand-total">
                            { score.getRunningTotal() }
                        </div>
                        <div className="archers__score__grand-total">
                            { score.getGoldCount() }
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
