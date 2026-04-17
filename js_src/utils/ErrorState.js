import React from 'react';


const ErrorState = ({ error }) => {
    return (
        <div className="error-state">
            <h1 className="error-state__heading">It’s a miss!</h1>
            <p>Something has gone wrong. Try refreshing the page?</p>
            <p>Sorry!</p>
            <p>&nbsp;</p>
            <p>Info for nerds:</p>
            <pre>{ error && error.message || 'No info?' }</pre>
        </div>
    );
};

export default ErrorState;
