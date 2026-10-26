import React, { useState } from 'react';

import { ErrorBoundary } from 'react-error-boundary';

import useQuery from '../utils/useQuery';
import ErrorState from '../utils/ErrorState';
import Spinner from '../utils/Spinner';

import ResultsNav from './ResultsNav';
import ResultList from './ResultList';


const ResultsPage = ({ resultsApi }) => {
    const [data, loading] = useQuery(resultsApi);
    const [selectedCategory, setSelectedCategory] = useState(null);

    if (loading) {
        return (
            <div className="loading">
                <Spinner />
            </div>
        );
    }

    console.log(data);

    const title = data.resultsStatus.leaderboard ? 'Leaderboard' : 'Results';

    const links = data.formats.filter(format => format.id !== 'html').map(format => {
        return <a className="results-nav__category" key={ format.id } href={ format.url }>{ format.label }</a>;
    });

    const results = [];
    data.results.forEach(({ section, categories }) => {
        const sectionId = section.round.codename;
        categories.forEach(({ category, scores }) => {
            const resultsetId = `${sectionId}-${category.slug}`;
            if (selectedCategory && selectedCategory !== resultsetId) {
                return;
            }
            results.push(
                <ResultList
                    key={ resultsetId }
                    id={ resultsetId }
                    scores={ scores }
                    label={ category.name }
                    headers={ section.headers }
                />
            );
        });
    });

    return (
        <ErrorBoundary FallbackComponent={ ErrorState }>
            <div className="results-page">
                <nav className="results-page__nav">
                    <h3>{ title }</h3>
                    <ResultsNav mode={ data.mode } sections={ data.results } selectedCategory={ selectedCategory } setSelectedCategory={ setSelectedCategory } />
                    <div className="results-nav">
                        <div className="results-nav__label">Downloadable results</div>
                        { links }
                    </div>
                </nav>
                <article className="results-page__main">
                    { results }
                </article>
            </div>
        </ErrorBoundary>
    );
};

export default ResultsPage;
