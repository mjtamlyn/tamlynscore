import React from 'react';


const ResultsHeaders = ({ headers }) => {
    const labels = headers.map((header) => <div className="results_list__heading" key={ header }>{ header }</div>);
    return <>{ labels }</>;
};

const Result = ({ details, headers }) =>{
    const items = Iterator.zip([details, headers]).toArray();
    const bits = items.map(([detail, id]) => <div className="results_list__part" key={ id }>{ detail }</div>);
    return <>{ bits }</>;
};


const ResultList = ({ label, headers, scores }) => {
    const results = scores.map((score, index) => {
        return <Result details={ score } headers={ headers } key={ index } />
    });

    console.log(results);

    return (
        <div className="results_list">
            <h3>{ label }</h3>
            <div className="results_list__grid" style={ { display: 'grid', gridTemplateColumns: 'repeat(' + headers.length + ', 1fr)' } }>
                <ResultsHeaders headers={ headers } />
                { results }
            </div>
        </div>
    );
};

export default ResultList;
