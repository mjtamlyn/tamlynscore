import React from 'react';
import PropTypes from 'prop-types';


const EventHeader = ({ round, endNumber }) => {
    return (
        <div className="scoring-header">
            <h3>{ round }</h3>
            <h3>End { endNumber }</h3>
        </div>
    );
};
EventHeader.propTypes = {
    round: PropTypes.string.isRequired,
    endNumber: PropTypes.number.isRequired,
};

export default EventHeader;
