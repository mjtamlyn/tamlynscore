import React from 'react';

import ArcherRowDetails from './ArcherRowDetails';
import { getEnd, getEndScore, getGoldCount, getRunningTotal } from './utils';


const ScoreSheet = ({ score, toSummary }) => {
    const ends = [...Array(score.endCount).keys()];
    const arrowNumbers = [...Array(score.endLength).keys()];
    const scoreRows = ends.map((endNumber) => {
        const end = getEnd(score, endNumber + 1);
        const arrows = arrowNumbers.map(index => <div key={ `${endNumber}|${index}` }>{ end[index] || '-' }</div>);
        return [
            ...arrows,
            <div className="archers__score__total" key={ `${endNumber}|end` }>{ getEndScore(score, endNumber + 1) }</div>,
            <div className="archers__score__total" key={ `${endNumber}|golds` }>{ getGoldCount(score, endNumber + 1) }</div>,
            <div className="archers__score__total" key={ `${endNumber}|rt` }>{ getRunningTotal(score, endNumber + 1) }</div>,
        ];
    });

    const columnsCount = score.endLength + 3;

    return (
        <>
            <div className="full-height-page__card">
                <div className="archers__row">
                    <ArcherRowDetails score={ score } />
                    <div className="archers__score" style={ { gridTemplateColumns: `repeat(${columnsCount}, 1fr)`} }>
                        <div className="archers__score__heading archers__score__heading--span" style={ { gridColumnEnd: `span ${score.endLength}` } }>Arrows</div>
                        <div className="archers__score__heading">S</div>
                        <div className="archers__score__heading">10s</div>
                        <div className="archers__score__heading">RT</div>
                        { scoreRows }
                        <div style={ { gridColumnEnd: `span ${score.endLength}` } } />
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
