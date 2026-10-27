import React, { useState } from 'react';

import ScoreSheetPage from '../input/ScoreSheetPage';


const ResultsHeaders = ({ headers, team }) => {
    const labels = headers.map((header) => {
        var className = "results-list__heading"
        // TODO: Make this less hacky!
        if (header === "Archer" || header === "Club") {
            className += " results-list__heading--left";
        }
        return (
            <div className={ className } key={ header }>{ header }</div>
        );
    });
    return <>
        { labels }
        { !team && <div className="results-list__heading"/> }
    </>;
};

const Result = ({ details, team, scoresheetUrl, scoresheetApi, headers }) =>{
    const [showScoresheet, setShowScoresheet] = useState(false);

    const baseClassName = "results-list__part";

    const items = Iterator.zip([details, headers]).toArray();
    const bits = items.map(([detail, id]) => {
        var className = baseClassName;
        if (id === "Archer" || id === "Club") {
            className += ` ${baseClassName}--left`;
            if (team) {
                className += ` ${baseClassName}--team-name`;
            }
        }
        if (team) {
            className += ` ${baseClassName}--team-row`;
        }
        return (
            <div className={ className } key={ id }>{ detail }</div>
        );
    });

    if (team) {
        team.forEach((archer, index) => {
            var className = baseClassName;
            if (index !== team.length - 1) {
                className += ` ${baseClassName}--team-row`;
            }
            bits.push(<div className={ className }></div>);
            bits.push(<div className={ `${className} ${baseClassName}--left` }>{ archer[0] }</div>);
            archer.slice(1).forEach((detail) => {
                bits.push(
                    <div className={ className }>{ detail }</div>
                );
            });
        });
    }

    const toggleScoresheet = (e) => {
        e.preventDefault();
        setShowScoresheet(!showScoresheet);
    }
    var scoresheet = null;
    if (showScoresheet && scoresheetApi) {
        scoresheet = (
            <div className="results-list__score-sheet-row">
                <ScoreSheetPage scoreApi={ scoresheetApi } showHeaders={ false } />
            </div>
        );
    }

    return <>
        { bits }
        { !team && <div className="results-list__part">
            { scoresheetUrl && <a href={ scoresheetUrl } onClick={ toggleScoresheet } className="results-list__score-sheet" /> }
        </div> }
        { scoresheet }
    </>;
};


const ResultList = ({ label, headers, scores }) => {
    const results = scores.map((score, index) => {
        return (
            <Result
                details={ score.details }
                scoresheetUrl={ score.scoresheetUrl }
                scoresheetApi={ score.scoresheetApi }
                team={ score.team }
                headers={ headers }
                key={ index }
            />
        );
    });

    // TODO: Make header types richer so we can build this
    const templateColumns = `min-content 2fr ${scores[0].team ? '' : '1fr '}repeat(${headers.length - 2}, min-content)`;
    return (
        <div className="results-list">
            <h3>{ label }</h3>
            <div className="results-list__grid" style={ { gridTemplateColumns: templateColumns } }>
                <ResultsHeaders headers={ headers } team={ !!scores[0].team }  />
                { results }
            </div>
        </div>
    );
};

export default ResultList;
