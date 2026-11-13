import React from 'react';

import { ErrorBoundary } from 'react-error-boundary';

import { useQuery } from '@tanstack/react-query';

import { CompetitionContext } from '../context/CompetitionContext';
import ErrorState from '../utils/ErrorState';
import Spinner from '../utils/Spinner';

import RegistrationFilter from './RegistrationFilter';
import RegistrationTargetList from './RegistrationTargetList';

const RegistrationPage = ({ targetListApi }) => {
    const { isPending, isError, data, error } = useQuery({ 
        queryKey: ['targetList'],
        queryFn: async () => {
            const response = await fetch(targetListApi);
            if (!response.ok || response.status !== 200) {
                throw new Error('TargetList API failed');
            }
            return response.json();
        },
        refetchInterval: 3 * 1000,  // 3 seconds
    });

    if (isPending) {
        return (
            <div className="loading">
                <Spinner />
            </div>
        );
    }

    if (isError) {
        return <ErrorState error={ error } />;
    }

    return (
        <ErrorBoundary FallbackComponent={ ErrorState }>
            <CompetitionContext.Provider value={ data.competition }>
                <h2>Registration</h2>
                <RegistrationFilter sessions={ data.targetList } />
                <RegistrationTargetList targetList={ data.targetList } />
            </CompetitionContext.Provider>
        </ErrorBoundary>
    );
};

export default RegistrationPage;
