import React from 'react';


const EventHeader = ({ round, pageTitle, setPageRoot }) => {
    return (
        <div className="scoring-header">
            <h3 onClick={ setPageRoot }>{ round }</h3>
            <h3>{ pageTitle }</h3>
        </div>
    );
};

export default EventHeader;
