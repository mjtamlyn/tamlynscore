import React, { useState } from 'react';

import Score from '../models/Score';

import EventHeader from './EventHeader';
import ScoresOverview from './ScoresOverview';
import TargetInput from './TargetInput';


const Target = ({ session, scores }) => {
    const modelScores = scores.map(score => new Score(score));
    const [endNumber, setEndNumber] = useState(Math.min(...modelScores.map(score => score.currentEnd())));
    const maxEnds = 20;
    const [page, setPage] = useState('overview');

    let startNextEnd = null;
    let complete = null;
    if (!modelScores.some(score => !score.isEndComplete(endNumber))) {
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
                <ScoresOverview scores={ modelScores } endNumber={ endNumber } continueEnd={ continueEnd } startNextEnd={ startNextEnd } complete={ complete } />
            </div>
        );
    } else if (page === 'input') {
        return (
            <div className="full-height-page">
                <EventHeader round={ session.round } pageTitle={ 'End ' + endNumber } />
                <TargetInput scores={ modelScores } endNumber={ endNumber } toSummary={ () => setPage('overview') } />
            </div>
        );
    }
};

export default Target;
