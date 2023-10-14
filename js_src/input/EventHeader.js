import React from 'react';
import PropTypes from 'prop-types';


const EventHeader = ({ round, pageTitle }) => {
    return (
        <div className="scoring-header">
            <h3>{ round }</h3>
            <h3>{ pageTitle }</h3>
        </div>
    );
};
EventHeader.propTypes = {
    round: PropTypes.string.isRequired,
    pageTitle: PropTypes.string.isRequired,
};

export default EventHeader;
