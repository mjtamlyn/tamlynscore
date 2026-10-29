import React from 'react';

import { ErrorBoundary } from 'react-error-boundary';

import { useQuery } from '@tanstack/react-query'

import ErrorState from '../utils/ErrorState';
import Spinner from '../utils/Spinner';

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
            <h3>Inspection React!</h3>
            <p>{ JSON.stringify(data) }</p>
        </ErrorBoundary>
    );
};

export default EquipmentInspectionPage;
