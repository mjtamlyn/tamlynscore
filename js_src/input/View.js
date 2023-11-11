import React, { useState, useEffect } from 'react';

import FullPageWrapper from './FullPageWrapper';
import FullPageLoading from '../utils/FullPageLoading';


const View = ({ api, render }) => {
    const [loaded, setLoaded] = useState(false);
    const [data, setData] = useState(null);

    useEffect(() => {
        if (!loaded) {
            fetch(api).then(response => response.json()).then(data => {
                setLoaded(true);
                setData(data);
            });
        }
    }, [api, loaded]);

    if (!loaded) {
        return <FullPageLoading />
    }
    return (
        <FullPageWrapper>
            { render(data) }
        </FullPageWrapper>
    );
};

export default View;
