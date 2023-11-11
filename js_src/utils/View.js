import React, { useState, useEffect } from 'react';


const View = ({ api, render, Loading }) => {
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
        return (
            <Loading />
        );
    }
    return render(data);
};

export default View;