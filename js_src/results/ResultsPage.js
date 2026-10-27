import React, { useState } from 'react';

import { ErrorBoundary } from 'react-error-boundary';
import { useMediaQuery } from 'react-responsive';

import useQuery from '../utils/useQuery';
import ErrorState from '../utils/ErrorState';
import Spinner from '../utils/Spinner';

import ResultsNav from './ResultsNav';
import ResultList from './ResultList';


const ResultsPage = ({ resultsApi }) => {
    const [data, loading] = useQuery(resultsApi);
    const isNarrow = useMediaQuery({ query: '(max-width: 950px)' });
    const [selectedCategory, setSelectedCategory] = useState(null);
    const [navOpen, setNavOpen] = useState(true);

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

    const results = [];
    data.results.forEach(({ section, categories }) => {
        categories.forEach(({ category, scores }) => {
            const resultsetId = `${section.id}-${category.slug}`;
            if (selectedCategory && selectedCategory !== resultsetId) {
                return;
            }
            var label = category.name;
            if (!selectedCategory && data.results.length > 1) {
                label = `${section.round.label} - ${category.name}`;
            }
            results.push(
                <ResultList
                    key={ resultsetId }
                    id={ resultsetId }
                    scores={ scores }
                    label={ label }
                    headers={ section.headers }
                />
            );
        });
    });

    var content = null;
    if (isNarrow) {
        if (navOpen) {
            const setCategory = (category) => {
                setNavOpen(false);
                setSelectedCategory(category)
            };
            content = (
                <nav className="results-page__nav results-page__nav--full-width">
                    <h3>{ title }</h3>
                    <ResultsNav 
                        mode={ data.mode }
                        sections={ data.results }
                        selectedCategory={ selectedCategory }
                        setSelectedCategory={ setCategory }
                    />
                    <div className="results-nav">
                        <div className="results-nav__label">Downloadable results</div>
                        { links }
                    </div>
                </nav>
            );
        } else {
            content = (
                <article className="results-page__main results-page__main--full-width">
                    <a className="results-page__nav-toggle" onClick={ () => setNavOpen(true) }></a>
                    { results }
                </article>
            );
        }
    } else {
        content = (
            <div className="results-page__scroll">
                { navOpen && <nav className="results-page__nav">
                    <a className="results-page__nav-toggle" onClick={ () => setNavOpen(false) }></a>
                    <h3>{ title }</h3>
                    <ResultsNav 
                        mode={ data.mode }
                        sections={ data.results }
                        selectedCategory={ selectedCategory }
                        setSelectedCategory={ setSelectedCategory }
                    />
                    <div className="results-nav">
                        <div className="results-nav__label">Downloadable results</div>
                        { links }
                    </div>
                </nav> }
                <article className={ "results-page__main" + (!navOpen ? " results-page__main--full-width" : "") }>
                    { !navOpen &&
                        <a className="results-page__nav-toggle" onClick={ () => setNavOpen(true) }></a>
                    }
                    { results }
                </article>
            </div>
        );
    }

    return (
        <ErrorBoundary FallbackComponent={ ErrorState }>
            <div className="results-page">
                { content }
            </div>
        </ErrorBoundary>
    );
};

export default ResultsPage;
