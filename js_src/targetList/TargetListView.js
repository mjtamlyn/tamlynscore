import React from 'react';

import useQuery from '../utils/useQuery';
import { CompetitionContext } from '../context/CompetitionContext';
import { TargetListProvider } from '../context/TargetListContext';
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
        <CompetitionContext.Provider value={ data.competition }>
            <TargetListProvider api={ api } targetList={ data.targetList }>
                <TargetListEdit />
            </TargetListProvider>
        </CompetitionContext.Provider>
    );
}

export default TargetListView;
