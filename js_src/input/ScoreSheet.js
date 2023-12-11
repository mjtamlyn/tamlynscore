import React, { useContext, useState } from 'react';

import { CompetitionContext } from '../context/CompetitionContext';
import ArcherRowDetails from './ArcherRowDetails';
import { getEnd, getEndScore, getHitCount, getGoldCount, getXCount, getRunningTotal } from './utils';


const byEntered = 'byEntered';
const byDozen = 'byDozen';


const ScoreSheet = ({ score, showDetails }) => {
    const competition = useContext(CompetitionContext);
    const [displayMode, setDisplayMode] = useState(byEntered);

    const totalArrows = score.round.endCount * score.round.endLength;
    const endCount = (displayMode === byEntered) ? score.round.endCount : (totalArrows / 12);
    const endLength = (displayMode === byEntered) ? score.round.endLength : 12;

    let displayToggle = null;
    if (!(totalArrows % 12) && !(12 % score.round.endLength) && score.round.endLength < 12) {
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

        const totals = [
            <div className="archers__score__total" key={ `${endNumber}|end` }>{ getEndScore(score, endNumber + 1, endLength) }</div>
        ];
        if (score.round.resultsOptions.hasHits) {
            totals.push(
                <div className="archers__score__total" key={ `${endNumber}|hits` }>{ getHitCount(score, endNumber + 1, endLength) }</div>
            );
        }
        if (score.round.resultsOptions.hasGolds) {
            totals.push(
                <div className="archers__score__total" key={ `${endNumber}|golds` }>{ getGoldCount(score, endNumber + 1, endLength) }</div>
            )
        }
        if (score.round.resultsOptions.hasXs) {
            totals.push(
                <div className="archers__score__total" key={ `${endNumber}|xs` }>{ getXCount(score, endNumber + 1, endLength) }</div>
            );
        }
        totals.push(
            <div className="archers__score__total" key={ `${endNumber}|rt` }>{ getRunningTotal(score, endNumber + 1, endLength) }</div>
        )
        if (competition.isAdmin && displayMode === byEntered) {
            const href = `${competition.url}input-arrows/${score.sessionId}/doz${endNumber + 1}/boss${score.boss}/`;
            totals.push(
                <div key={ `${endNumber}|edit` }>
                    <a className="btn btn-small" href={ href }>Edit</a>
                </div>
            );
        }
        return [
            ...arrows,
            ...totals,
        ];
    });

    let headings = [
        <div className="archers__score__heading archers__score__heading--span" style={ { gridColumnEnd: `span ${endLength}` } } key="arrows">Arrows</div>
    ];
    if (endLength === 12) {
        headings = [
            <div className="archers__score__heading archers__score__heading--span" style={ { gridColumnEnd: `span 6` } } key="arrows-1">Arrows</div>,
            <div className="archers__score__heading" key="et-1">ET</div>,
            <div className="archers__score__heading archers__score__heading--span" style={ { gridColumnEnd: `span 6` } } key="arrows-2">Arrows</div>,
            <div className="archers__score__heading" key="et-2">ET</div>,
        ];
    }
    headings.push(
        <div className="archers__score__heading" key="S">S</div>
    );
    score.round.resultsOptions.scoringHeadings.forEach(heading => {
        headings.push(
            <div className="archers__score__heading" key={ heading }>{ heading }</div>
        );
    });
    headings.push(
        <div className="archers__score__heading" key="RT">RT</div>
    );
    if (competition.isAdmin && displayMode === byEntered) {
        headings.push(<div className="archers__score__heading">Edit</div>);
    }

    const columnsCount = endLength + 2 + score.round.resultsOptions.scoringHeadings.length + (endLength === 12 ? 2 : 0) + ((competition.isAdmin && displayMode === byEntered) ? 1 : 0);
    const totalsPadding = endLength === 12 ? 14 : endLength

    const splits = [];
    score.round.splits.forEach((split, index) => {
        // TODO: at the moment this assumes the splits are the same length. Will fail on Yorks/Bristols.
        splits.push(
            <div style={ { gridColumnEnd: `span ${totalsPadding - 1}` } } key={ `${split.name}|padding` } />,
            <div className="archers__score__split-title" key={ `${split.name}|name` }>{ split.name }</div>,
            <div className="archers__score__grand-total" key={ `${split.name}|score` }>{ getEndScore(score, index + 1, split.arrows) }</div>,
        );
        if (score.round.resultsOptions.hasHits) {
            splits.push(
                <div className="archers__score__grand-total" key={ `${split.name}|hits` }>
                    { getHitCount(score, index + 1, split.arrows) }
                </div>
            );
        }
        if (score.round.resultsOptions.hasGolds) {
            splits.push(
                <div className="archers__score__grand-total" key={ `${split.name}|golds` }>
                    { getGoldCount(score, index + 1, split.arrows) }
                </div>
            );
        }
        if (score.round.resultsOptions.hasXs) {
            splits.push(
                <div className="archers__score__grand-total" key={ `${split.name}|xs` }>
                    { getXCount(score, index + 1, split.arrows) }
                </div>
            );
        }
        splits.push(
            <div key={ `${split.name}|padding2` }></div>,
        );
    });

    return (
        <>
            { displayToggle && 
                <div className="archers__score-display-toggle">
                    Display in { displayToggle }
                </div>
            }
            <div className="archers__row archers__row--no-bg">
                { showDetails && <ArcherRowDetails score={ score } /> }
                <div className="archers__score" style={ { gridTemplateColumns: `repeat(${columnsCount}, 1fr)`} }>
                    { headings }
                    { scoreRows }
                    <div style={ { gridColumnEnd: `span ${totalsPadding}` } } />
                    <div className="archers__score__grand-total">
                        { getRunningTotal(score) }
                    </div>
                    { score.round.resultsOptions.hasHits &&
                        <div className="archers__score__grand-total">
                            { getHitCount(score) }
                        </div>
                    }
                    { score.round.resultsOptions.hasGolds &&
                        <div className="archers__score__grand-total">
                            { getGoldCount(score) }
                        </div>
                    }
                    { score.round.resultsOptions.hasXs &&
                        <div className="archers__score__grand-total">
                            { getXCount(score) }
                        </div>
                    }
                    <div></div>
                    { splits }
                </div>
            </div>
        </>
    );
};

export default ScoreSheet;
