import React, { useState } from 'react';

import Score from '../models/Score';
import Store from '../models/Store';

import useQuery from '../utils/useQuery';
import FullPageLoading from '../utils/FullPageLoading';
import FullPageWrapper from '../utils/FullPageWrapper';

import SessionList from './SessionList';
import Target from './Target';


const SessionListPage = ({ api, setPage }) => {
    const [data, loading] = useQuery(api);
    if (loading) return <FullPageLoading />;

    return (
        <FullPageWrapper competition={ data.competition }>
            <SessionList sessions={ data.sessions } user={ data.user } competition={ data.competition } setPage={ setPage } />
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
            <Target
                session={ data.session }
                user={ data.user }
                competition={ data.competition }
                scores={ store.data }
                store={ store }
                setPageRoot={ () => setPage({name: 'root', api: '/scoring/api/' }) }
            />
        </FullPageWrapper>
    );
};


const InputController = () => {
    const [page, setPage] = useState({
        'name': 'root',
        'api': '/scoring/api/',
    });

    if (page.name === 'root') {
        return <SessionListPage api={ page.api } setPage={ setPage } />;
    } else {
        return <TargetPage api={ page.api } setPage={ setPage } />;
    }
};

export default InputController;
