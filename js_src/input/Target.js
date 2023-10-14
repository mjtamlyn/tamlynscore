import React, { useState } from 'react';

import Score from '../models/Score';

import EventHeader from './EventHeader';
import ScoresOverview from './ScoresOverview';
import TargetInput from './TargetInput';


const scoreA = new Score({
    target: '1A',
    name: 'Nicola Wood',
    categories: {
        bowstyle: 'Compound',
        gender: 'Women',
    },
    arrows: [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 9, 9, 10, 10, 9, 10, 9, 8],
});
const scoreB = new Score({
    target: '1B',
    name: 'Antony Wood',
    categories: {
        bowstyle: 'Recurve',
        gender: 'Men',
    },
    arrows: [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 9, 9, 10, 10, 9, 10],
});
const scoreC = new Score({
    target: '1C',
    name: 'Hannah Brown',
    categories: {
        bowstyle: 'Compound',
        gender: 'Women',
    },
    arrows: [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 9, 10, 10, 9],
});
const scoreD = new Score({
    target: '1D',
    name: 'Steve Mitchell',
    categories: {
        bowstyle: 'Compound',
        gender: 'Men',
    },
    arrows: [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 9, 9, 10, 10, 9],
});
const scores = [scoreA, scoreB, scoreC, scoreD];

const Target = () => {
    const [endNumber, setEndNumber] = useState(9);
    const maxEnds = 10;
    const [page, setPage] = useState('overview');

    let startNextEnd = null;
    let complete = null;
    if (scoreA.isEndComplete(endNumber) &&
            scoreB.isEndComplete(endNumber) &&
            scoreC.isEndComplete(endNumber) &&
            scoreD.isEndComplete(endNumber)
    ) {
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
                <EventHeader round="WA 18" pageTitle="Overview" />
                <ScoresOverview scores={ scores } endNumber={ endNumber } continueEnd={ continueEnd } startNextEnd={ startNextEnd } complete={ complete } />
            </div>
        );
    } else if (page === 'input') {
        return (
            <div className="full-height-page">
                <EventHeader round="WA 18" pageTitle={ 'End ' + endNumber } />
                <TargetInput scores={ scores } endNumber={ endNumber } toSummary={ () => setPage('overview') } />
            </div>
        );
    }
};

export default Target;
