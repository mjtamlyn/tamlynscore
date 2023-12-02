import React, { useState } from 'react';

import { ErrorBoundary } from 'react-error-boundary';

import Score from '../models/Score';
import Store from '../models/Store';

import { CompetitionContext } from '../context/CompetitionContext';
import useQuery from '../utils/useQuery';
import FullPageLoading from '../utils/FullPageLoading';
import FullPageWrapper from '../utils/FullPageWrapper';
import ErrorState from '../utils/ErrorState';

import SessionList from './SessionList';
import Target from './Target';


const SessionListPage = ({ api, setPage }) => {
    const [data, loading] = useQuery(api);
    if (loading) return <FullPageLoading />;

    return (
        <FullPageWrapper competition={ data.competition }>
            <ErrorBoundary FallbackComponent={ ErrorState }>
                <CompetitionContext.Provider value={ data.competition }>
                    <SessionList sessions={ data.sessions } user={ data.user } setPage={ setPage } />
                </CompetitionContext.Provider>
            </ErrorBoundary>
        </FullPageWrapper>
    );
};


const TargetPage = ({ api, setPage }) => {
    const [data, loading] = useQuery(api);
    if (loading) return <FullPageLoading />;

    const scores = data.scores.map(score => new Score({ ...score }));
    const store = new Store({ api: api, data: scores, dataName: 'scores' });
    return (
        <FullPageWrapper competition={ data.competition }>
            <ErrorBoundary FallbackComponent={ ErrorState }>
                <CompetitionContext.Provider value={ data.competition }>
                    <Target
                        session={ data.session }
                        user={ data.user }
                        scores={ store.data }
                        store={ store }
                        setPageRoot={ () => setPage({name: 'root', api: '/scoring/api/' }) }
                    />
                </CompetitionContext.Provider>
            </ErrorBoundary>
        </FullPageWrapper>
    );
};


const InputController = () => {
    const [page, setPage] = useState({
        'name': 'root',
        'api': '/scoring/api/',
    });

    let content = null;
    if (page.name === 'root') {
        content = <SessionListPage api={ page.api } setPage={ setPage } />;
    } else {
        content = <TargetPage api={ page.api } setPage={ setPage } />;
    }

    return (
        <ErrorBoundary FallbackComponent={ ErrorState }>
            { content }
        </ErrorBoundary>
    );
};

export default InputController;
