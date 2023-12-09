import React, { useState } from 'react';

import ArcherRowDetails from './ArcherRowDetails';
import { getEnd, getEndScore, getGoldCount, getRunningTotal } from './utils';


const byEntered = 'byEntered';
const byDozen = 'byDozen';


const ScoreSheet = ({ score, toSummary }) => {
    const [displayMode, setDisplayMode] = useState(byEntered);

    const totalArrows = score.round.endCount * score.round.endLength;
    const endCount = (displayMode === byEntered) ? score.round.endCount : (totalArrows / 12);
    const endLength = (displayMode === byEntered) ? score.round.endLength : 12;

    let displayToggle = null;
    if (!(totalArrows % 12) && score.round.endLength < 12) {
        const toggleDisplayMode = (e) => {
            e.preventDefault();
            if (displayMode === byEntered) {
                setDisplayMode(byDozen);
            } else {
                setDisplayMode(byEntered);
            }
        };
        displayToggle = (
            <a onClick={ toggleDisplayMode } className="btn btn-small btn-toggle archers__score__toggle">
                <div className={ 'btn-segment ' + (displayMode === byEntered ? 'selected' : '') }>{ score.round.endLength }s</div>
                <div className={ 'btn-segment ' + (displayMode === byDozen ? 'selected' : '') }>12s</div>
            </a>
        );
    }

    const ends = [...Array(endCount).keys()];
    const arrowNumbers = [...Array(endLength).keys()];

    const scoreRows = ends.map((endNumber) => {
        const end = getEnd(score, endNumber + 1, endLength);

        const arrows = [];
        if (endLength === 12) {
            arrows.push(...arrowNumbers.slice(0, 6).map(index => <div key={ `${endNumber}|${index}` }>{ end[index] || '-' }</div>));
            arrows.push(<div className="archers__score__total" key={ `${endNumber}|end-total-1` }>{ getEndScore(score, (endNumber + 1) * 2 - 1, 6) }</div>)
            arrows.push(...arrowNumbers.slice(6, 12).map(index => <div key={ `${endNumber}|${index + 6}` }>{ end[index] || '-' }</div>));
            arrows.push(<div className="archers__score__total" key={ `${endNumber}|end-total-2` }>{ getEndScore(score, (endNumber + 1) * 2, 6) }</div>)
        } else {
            arrows.push(...arrowNumbers.map(index => <div key={ `${endNumber}|${index}` }>{ end[index] || '-' }</div>));
        }

        return [
            ...arrows,
            <div className="archers__score__total" key={ `${endNumber}|end` }>{ getEndScore(score, endNumber + 1, endLength) }</div>,
            <div className="archers__score__total" key={ `${endNumber}|golds` }>{ getGoldCount(score, endNumber + 1, endLength) }</div>,
            <div className="archers__score__total" key={ `${endNumber}|rt` }>{ getRunningTotal(score, endNumber + 1, endLength) }</div>,
        ];
    });

    const columnsCount = endLength + 3 + (endLength === 12 ? 2 : 0);

    let arrowsHeading = (
        <div className="archers__score__heading archers__score__heading--span" style={ { gridColumnEnd: `span ${endLength}` } }>Arrows</div>
    );
    if (endLength === 12) {
        arrowsHeading = <>
            <div className="archers__score__heading archers__score__heading--span" style={ { gridColumnEnd: `span 6` } }>Arrows</div>
            <div className="archers__score__heading">ET</div>
            <div className="archers__score__heading archers__score__heading--span" style={ { gridColumnEnd: `span 6` } }>Arrows</div>
            <div className="archers__score__heading">ET</div>
        </>;
    }

    return (
        <>
            <div className="full-height-page__card">
                { displayToggle && 
                    <div className="archers__score-display-toggle">
                        Display in { displayToggle }
                    </div>
                }
                <div className="archers__row">
                    <ArcherRowDetails score={ score } />
                    <div className="archers__score" style={ { gridTemplateColumns: `repeat(${columnsCount}, 1fr)`} }>
                        { arrowsHeading }
                        <div className="archers__score__heading">S</div>
                        <div className="archers__score__heading">10s</div>
                        <div className="archers__score__heading">RT</div>
                        { scoreRows }
                        <div style={ { gridColumnEnd: `span ${endLength === 12 ? 14 : endLength}` } } />
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
