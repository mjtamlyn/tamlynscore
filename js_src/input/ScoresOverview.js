import React from 'react';

import ArcherRowSummary from './ArcherRowSummary';


const ScoresOverview = ({ scores, endNumber, continueEnd, startNextEnd, complete }) => {
    const [scoreA, scoreB, scoreC, scoreD] = scores;
    return (
        <>
            <div className="archers">
                <ArcherRowSummary score={ scoreA } />
                <ArcherRowSummary score={ scoreB } />
                <ArcherRowSummary score={ scoreC } />
                <ArcherRowSummary score={ scoreD } />
            </div>
            <div className="actions">
                { continueEnd && <div className="actions__button" onClick={ continueEnd }>
                    Edit end { endNumber }
                </div> }
                { startNextEnd && <div className="actions__button" onClick={ startNextEnd }>
                    Start end { endNumber + 1 }
                </div> }
                { complete && <div className="actions__button" onClick={ complete }>
                    Confirm final scores
                </div> }
            </div>
        </>
    );
};

export default ScoresOverview;
