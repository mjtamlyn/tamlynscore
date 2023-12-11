import React from 'react';

import { ErrorBoundary } from 'react-error-boundary';

import useQuery from '../utils/useQuery';
import { CompetitionContext } from '../context/CompetitionContext';
import ErrorState from '../utils/ErrorState';
import Spinner from '../utils/Spinner';

import ScoreSheet from './ScoreSheet';


const ScoreSheetPage = ({ scoreApi }) => {
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

    return (
        <ErrorBoundary FallbackComponent={ ErrorState }>
            <CompetitionContext.Provider value={ data.competition }>
                <div id="target-input">
                    <ScoreSheet score={ score } />
                </div>
            </CompetitionContext.Provider>
        </ErrorBoundary>
    );
};

export default ScoreSheetPage;
