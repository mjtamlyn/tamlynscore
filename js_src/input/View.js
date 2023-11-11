import React, { useState, useEffect } from 'react';


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
        return (
            <div className="full-height-page">
                <nav className="header-nav">
                    <div className="container">
                        <div className="home">
                            <a href="/" className="wide">TamlynScore</a>
                            <a href="/" className="narrow">TS</a>
                        </div>
                    </div>
                </nav>
                <div className="full-height-page__loading">Loading...</div>
            </div>
        );
    }
    return (
        <div className="full-height-page">
            <nav className="header-nav">
                <div className="container">
                    <div className="home">
                        <a href="/" className="wide">TamlynScore</a>
                        <a href="/" className="narrow">TS</a>
                    </div>
                    <h2 className="header-title"><a href={ data.competition.url }>{ data.competition.short }</a></h2>
                </div>
            </nav>
            <div className="full-height-page__content">
                { render(data) }
            </div>
        </div>
    );
};

export default View;
