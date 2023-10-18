import React, { useState } from 'react';

import Store from '../models/Store';

import SessionList from './SessionList';
import Target from './Target';
import View from './View';


const InputController = () => {
    const [page, setPage] = useState({
        'name': 'root',
        'api': '/scoring/js/api/',
    });

    if (page.name === 'root') {
        return (
            <View api={ page.api } render={ data => <SessionList sessions={ data.sessions } user={ data.user } competition={ data.competition } setPage={ setPage } /> } key={ page.name } />
        );
    } else {
        return (
            <View api={ page.api } render={ data => {
                const store = new Store({ api: page.api, scores: data.scores });
                return (
                    <Target
                        session={ data.session }
                        user={ data.user }
                        competition={ data.competition }
                        scores={ store.scores }
                        store={ store }
                        setPage={ setPage }
                        key={ page.name }
                    />
                );
            } } />
        );
    }
};

export default InputController;
