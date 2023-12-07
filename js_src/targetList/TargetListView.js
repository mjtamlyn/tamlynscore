import React from 'react';

import { ErrorBoundary } from 'react-error-boundary';

import useQuery from '../utils/useQuery';
import { CompetitionContext } from '../context/CompetitionContext';
import { TargetListProvider } from '../context/TargetListContext';
import ErrorState from '../utils/ErrorState';
import Spinner from '../utils/Spinner';

import TargetListEdit from './TargetListEdit';

const TargetListView = ({ api }) => {
    const [data, loading] = useQuery(api);

    if (loading) {
        return (
            <div className="target-list module">
                <h2>Target List</h2>
                <div className="loading">
                    <Spinner />
                </div>
            </div>
        );
    }

    return (
        <ErrorBoundary FallbackComponent={ ErrorState }>
            <CompetitionContext.Provider value={ data.competition }>
                <TargetListProvider api={ api } targetList={ data.targetList }>
                    <TargetListEdit />
                </TargetListProvider>
            </CompetitionContext.Provider>
        </ErrorBoundary>
    );
}

export default TargetListView;
