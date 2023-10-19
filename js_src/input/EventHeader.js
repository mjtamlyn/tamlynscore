import React from 'react';
import PropTypes from 'prop-types';


const EventHeader = ({ round, pageTitle, setPageRoot }) => {
    return (
        <div className="scoring-header">
            <h3 onClick={ setPageRoot }>{ round }</h3>
            <h3>{ pageTitle }</h3>
        </div>
    );
};
EventHeader.propTypes = {
    round: PropTypes.string.isRequired,
    pageTitle: PropTypes.string.isRequired,
};

export default EventHeader;
