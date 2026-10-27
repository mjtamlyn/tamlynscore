import React from 'react';

import { ErrorBoundary } from 'react-error-boundary';

import useQuery from '../utils/useQuery';
import { CompetitionContext } from '../context/CompetitionContext';
import ErrorState from '../utils/ErrorState';
import Spinner from '../utils/Spinner';

import ScoreSheet, { byDozen } from './ScoreSheet';


const ScoreSheetPage = ({ scoreApi, showHeaders = true }) => {
    const [data, loading] = useQuery(scoreApi);

    if (loading) {
        return (
            <div className="loading">
                <Spinner />
            </div>
        );
    }

    const score = data.score;
    score.round = data.round;
    score.sessionId = data.sessionId;

    return (
        <ErrorBoundary FallbackComponent={ ErrorState }>
            <CompetitionContext.Provider value={ data.competition }>
                { showHeaders && <h2>Scoresheet for { score.name }</h2> }
                { showHeaders && <h3>{ score.target } - { score.round.name }</h3> }
                <div className="target-input">
                    <ScoreSheet score={ score } initialDisplayMode={ byDozen } />
                </div>
            </CompetitionContext.Provider>
        </ErrorBoundary>
    );
};

export default ScoreSheetPage;
