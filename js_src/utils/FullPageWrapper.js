import React from 'react';


const FullPageWrapper = ({ children, competition }) => {
    return (
        <div className="full-height-page">
            <nav className="header-nav">
                <div className="container">
                    <div className="home">
                        <a href="/" className="wide">TamlynScore</a>
                        <a href="/" className="narrow">TS</a>
                    </div>
                    { competition && <h2 className="header-title"><a href={ competition.url }>{ competition.short }</a></h2> }
                </div>
            </nav>
            <div className="full-height-page__content">
                { children }
            </div>
        </div>
    );
};

export default FullPageWrapper;
