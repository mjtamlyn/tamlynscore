import React from 'react';

import { ErrorBoundary } from 'react-error-boundary';

import useQuery from '../utils/useQuery';
import ErrorState from '../utils/ErrorState';
import Spinner from '../utils/Spinner';

import SectionSelector from './SectionSelector';
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
    console.log(data);

    const title = data.resultsStatus.leaderboard ? 'Leaderboard' : 'Results';

    const links = data.formats.filter(format => format.id !== 'html').map(format => {
        return <a key={ format.id } href={ format.url } className="btn">{ format.label }</a>;
    });

    return <>
        <h2>{ title }</h2>
        <SectionSelector mode={ data.mode } sections={ data.results } />
        <h3>Downloadable results</h3>
        <div className="btn-list">
            { links }
        </div>
        <ResultList scores={ data.results[0].categories[0].scores } label={ data.results[0].categories[0].category.name } headers={ data.results[0].section.headers } />
    </>;
};

export default ResultsPage;
