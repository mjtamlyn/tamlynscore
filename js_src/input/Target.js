import React, { useState } from 'react';

import EventHeader from './EventHeader';
import ScoresOverview from './ScoresOverview';
import TargetInput from './TargetInput';


const Target = ({ session, scores, store }) => {
    const [endNumber, setEndNumber] = useState(Math.min(...scores.map(score => score.currentEnd())));
    const maxEnds = 20;
    const [page, setPage] = useState('overview');

    let startNextEnd = null;
    let complete = null;
    if (!scores.some(score => !score.isEndComplete(endNumber))) {
        if (endNumber + 1 <= maxEnds) {
            startNextEnd = () => {
                setPage('input');
                setEndNumber(endNumber + 1);
            };
        } else {
            complete = () => {
                window.location = '/'
            };
        }
    }

    const continueEnd = () => {
        setPage('input');
    };

    if (page === 'overview') {
        return (
            <div className="full-height-page">
                <EventHeader round={ session.round } pageTitle="Overview" />
                <ScoresOverview scores={ scores } endNumber={ endNumber } continueEnd={ continueEnd } startNextEnd={ startNextEnd } complete={ complete } />
            </div>
        );
    } else if (page === 'input') {
        const toSummary = () => {
            setPage('overview');
            store.save();
        };
        return (
            <div className="full-height-page">
                <EventHeader round={ session.round } pageTitle={ 'End ' + endNumber } />
                <TargetInput scores={ scores } endNumber={ endNumber } toSummary={ toSummary } />
            </div>
        );
    }
};

export default Target;
