import React from 'react';


const ResultsHeaders = ({ headers }) => {
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
        <div className="results-list__heading"/>
    </>;
};

const Result = ({ details, headers }) =>{
    const items = Iterator.zip([details, headers]).toArray();
    const bits = items.map(([detail, id]) => {
        var className = "results-list__part"
        if (id === "Archer" || id === "Club") {
            className += " results-list__part--left";
        }
        return (
            <div className={ className } key={ id }>{ detail }</div>
        );
    });
    return <>
        { bits }
        <div className="results-list__part">
            <a className="results-list__score-sheet" />
        </div>
    </>;
};


const ResultList = ({ label, headers, scores }) => {
    const results = scores.map((score, index) => {
        return <Result details={ score } headers={ headers } key={ index } />
    });

    // TODO: Teams!
    
    // TODO: Make header types richer so we can build this
    const templateColumns = `30px 2fr 1fr repeat(${headers.length - 3}, 60px) 30px`;
    return (
        <div className="results-list">
            <h3>{ label }</h3>
            <div className="results-list__grid" style={ { gridTemplateColumns: templateColumns } }>
                <ResultsHeaders headers={ headers } />
                { results }
            </div>
        </div>
    );
};

export default ResultList;
