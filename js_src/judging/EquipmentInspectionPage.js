import React from 'react';

import { ErrorBoundary } from 'react-error-boundary';

import { useQuery } from '@tanstack/react-query'

import { CompetitionContext } from '../context/CompetitionContext';
import ErrorState from '../utils/ErrorState';
import Spinner from '../utils/Spinner';

import EquipmentInspection from './EquipmentInspection';


const EquipmentInspectionPage = ({ judgingApi, targetListApi }) => {
    const { isPending, isError, data, error } = useQuery({ 
        queryKey: ['targetList', targetListApi],
        queryFn: async () => {
            const response = await fetch(targetListApi);
            if (!response.ok) {
                throw new Error('Judge API failed', response);
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

    return (
        <ErrorBoundary FallbackComponent={ ErrorState }>
            <CompetitionContext.Provider value={ data.competition }>
                <EquipmentInspection targetList={ data.targetList } />
            </CompetitionContext.Provider>
        </ErrorBoundary>
    );
};

export default EquipmentInspectionPage;
