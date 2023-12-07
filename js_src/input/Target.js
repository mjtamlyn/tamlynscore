import React, { useContext, useState } from 'react';

import { InputScoresContext } from '../context/InputScoresContext';

import EventHeader from './EventHeader';
import ScoreSheet from './ScoreSheet';
import ScoresOverview from './ScoresOverview';
import StoreStatus from './StoreStatus';
import TargetInput from './TargetInput';

import { currentEnd, isEndComplete } from './utils';


const Target = ({ session, setPageRoot }) => {
    const scores = useContext(InputScoresContext).scores;

    const [endNumber, setEndNumber] = useState(Math.max(...scores.map(score => currentEnd(score))));
    const maxEnds = Math.max(...scores.map(score => score.endCount));
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
            </>
        );
    }

    let startNextEnd = null;
    let complete = null;
    if (!scores.some(score => !isEndComplete(score, endNumber))) {
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
            </>
        );
    } else if (subpage === 'input') {
        const toSummary = () => {
            setSubpage('overview');
            // TODO: store.save();
        };
        return (
            <>
                <EventHeader round={ session.round } pageTitle={ 'End ' + endNumber } setPageRoot={ setPageRoot } />
                <TargetInput scores={ scores } endNumber={ endNumber } toSummary={ toSummary } />
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
            </>
        );
    }
};

export default Target;
