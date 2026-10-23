import React from 'react';

import { ErrorBoundary } from 'react-error-boundary';

import useQuery from '../utils/useQuery';
import ErrorState from '../utils/ErrorState';
import Spinner from '../utils/Spinner';

import ResultsNav from './ResultsNav';
import ResultList from './ResultList';


const ResultsPage = ({ resultsApi }) => {
    const [data, loading] = useQuery(resultsApi);

    if (loading) {
        return (
            <div className="loading">
                <Spinner />
            </div>
        );
    }

    const title = data.resultsStatus.leaderboard ? 'Leaderboard' : 'Results';

    const links = data.formats.filter(format => format.id !== 'html').map(format => {
        return <a className="results-nav__category" key={ format.id } href={ format.url }>{ format.label }</a>;
    });

    return (
        <ErrorBoundary FallbackComponent={ ErrorState }>
            <div className="results-page">
                <nav className="results-page__nav">
                    <h3>{ title }</h3>
                    <ResultsNav mode={ data.mode } sections={ data.results } />
                    <div className="results-nav">
                        <div className="results-nav__label">Downloadable results</div>
                        { links }
                    </div>
                </nav>
                <article className="results-page__main">
                    <ResultList scores={ data.results[0].categories[0].scores } label={ data.results[0].categories[0].category.name } headers={ data.results[0].section.headers } />
                </article>
            </div>
        </ErrorBoundary>
    );
};

export default ResultsPage;
