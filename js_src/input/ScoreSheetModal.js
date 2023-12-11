import React from 'react';

import ScoreSheet from './ScoreSheet';


const ScoreSheetModal = ({ score, toSummary }) => {
    return (
        <>
            <div className="full-height-page__card">
                <ScoreSheet score={ score } showDetails />
                <div className="actions">
                    <a className="actions__button" onClick={ toSummary }>Back</a>
                </div>
            </div>
        </>
    );
};

export default ScoreSheetModal;
