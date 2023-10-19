import React, { useState } from 'react';

import EventHeader from './EventHeader';
import ScoresOverview from './ScoresOverview';
import StoreStatus from './StoreStatus';
import TargetInput from './TargetInput';


const Target = ({ session, scores, store, setPageRoot }) => {
    const [endNumber, setEndNumber] = useState(Math.min(...scores.map(score => score.currentEnd())));
    const maxEnds = 20;
    const [subpage, setSubpage] = useState('overview');

    let startNextEnd = null;
    let complete = null;
    if (!scores.some(score => !score.isEndComplete(endNumber))) {
        if (endNumber + 1 <= maxEnds) {
            startNextEnd = () => {
                setSubpage('input');
                setEndNumber(endNumber + 1);
            };
        } else {
            complete = setPageRoot;
        }
    }

    const continueEnd = () => {
        setSubpage('input');
    };

    if (subpage === 'overview') {
        return (
            <>
                <EventHeader round={ session.round } pageTitle="Overview" setPageRoot={ setPageRoot } />
                <ScoresOverview scores={ scores } endNumber={ endNumber } continueEnd={ continueEnd } startNextEnd={ startNextEnd } complete={ complete } />
                <StoreStatus store={ store } />
            </>
        );
    } else if (subpage === 'input') {
        const toSummary = () => {
            setSubpage('overview');
            store.save();
        };
        return (
            <>
                <EventHeader round={ session.round } pageTitle={ 'End ' + endNumber } setPageRoot={ setPageRoot } />
                <TargetInput scores={ scores } endNumber={ endNumber } toSummary={ toSummary } />
                <StoreStatus store={ store } />
            </>
        );
    }
};

export default Target;
