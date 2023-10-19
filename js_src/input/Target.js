import React, { useState } from 'react';

import EventHeader from './EventHeader';
import ScoreSheet from './ScoreSheet';
import ScoresOverview from './ScoresOverview';
import StoreStatus from './StoreStatus';
import TargetInput from './TargetInput';


const Target = ({ session, scores, store, setPageRoot }) => {
    const [endNumber, setEndNumber] = useState(Math.max(...scores.map(score => score.currentEnd())));
    const maxEnds = 20;
    const [subpage, setSubpage] = useState('overview');

    if (!scores.length) {
        return (
            <>
                <EventHeader round={ session.round } pageTitle="Overview" setPageRoot={ setPageRoot } />
                <div className="full-height-page__card">
                    No archers to enter - have you registered yet?
                    <div className="actions">
                        <a className="actions__button" onClick={ setPageRoot }>Back to session list</a>
                    </div>
                </div>
                <StoreStatus store={ store } />
            </>
        );
    }

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

    const showScoreSheet = (score) => {
        setSubpage({ name: 'scoresheet', score });
    };

    if (subpage === 'overview') {
        return (
            <>
                <EventHeader round={ session.round } pageTitle="Overview" setPageRoot={ setPageRoot } />
                <ScoresOverview scores={ scores } endNumber={ endNumber } continueEnd={ continueEnd } startNextEnd={ startNextEnd } complete={ complete } showScoreSheet={ showScoreSheet } />
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
    } else if (subpage.name === 'scoresheet') {
        const toSummary = () => {
            setSubpage('overview');
        };
        return (
            <>
                <EventHeader round={ session.round } pageTitle="Score sheet" setPageRoot={ setPageRoot } />
                <ScoreSheet score={ subpage.score } toSummary={ toSummary } />
                <StoreStatus store={ store } />
            </>
        );
    }
};

export default Target;
