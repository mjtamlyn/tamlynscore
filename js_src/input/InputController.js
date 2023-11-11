import React, { useState } from 'react';

import Score from '../models/Score';
import Store from '../models/Store';

import SessionList from './SessionList';
import Target from './Target';
import FullPageLoading from '../utils/FullPageLoading';
import FullPageWrapper from '../utils/FullPageWrapper';
import View from '../utils/View';


const InputController = () => {
    const [page, setPage] = useState({
        'name': 'root',
        'api': '/scoring/api/',
    });

    if (page.name === 'root') {
        return (
            <View api={ page.api } Loading={ FullPageLoading } render={
                data => {
                    return (
                        <FullPageWrapper competition={ data.competition }>
                            <SessionList sessions={ data.sessions } user={ data.user } competition={ data.competition } setPage={ setPage } />
                        </FullPageWrapper>
                    );
                }
            } key={ page.name } />
        );
    } else {
        return (
            <View api={ page.api } Loading={ FullPageLoading } render={ data => {
                const scores = data.scores.map(score => new Score({ ...score }));
                const store = new Store({ api: page.api, data: scores, dataName: 'scores' });
                return (
                    <FullPageWrapper competition={ data.competition }>
                        <Target
                            session={ data.session }
                            user={ data.user }
                            competition={ data.competition }
                            scores={ store.data }
                            store={ store }
                            setPageRoot={ () => setPage({name: 'root', api: '/scoring/api/' }) }
                            key={ page.name }
                        />
                    </FullPageWrapper>
                );
            } } />
        );
    }
};

export default InputController;
