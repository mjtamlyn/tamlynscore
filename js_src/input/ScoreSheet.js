import React from 'react';

import ArcherRowDetails from './ArcherRowDetails';
import { getEnd, getEndScore, getGoldCount, getRunningTotal } from './utils';


const ScoreSheet = ({ score, toSummary }) => {
    const ends = [...Array(20).keys()];
    const scoreRows = ends.map((endNumber) => {
        const end = getEnd(score, endNumber + 1);
        return [
            <div key={ `${endNumber}|1` }>{ end[0] || '-' }</div>,
            <div key={ `${endNumber}|2` }>{ end[1] || '-' }</div>,
            <div key={ `${endNumber}|3` }>{ end[2] || '-' }</div>,
            <div className="archers__score__total" key={ `${endNumber}|end` }>{ getEndScore(score, endNumber + 1) }</div>,
            <div className="archers__score__total" key={ `${endNumber}|golds` }>{ getGoldCount(score, endNumber + 1) }</div>,
            <div className="archers__score__total" key={ `${endNumber}|rt` }>{ getRunningTotal(score, endNumber + 1) }</div>,
        ];
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
                            { getRunningTotal(score) }
                        </div>
                        <div className="archers__score__grand-total">
                            { getGoldCount(score) }
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
