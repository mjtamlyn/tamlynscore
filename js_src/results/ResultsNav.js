import React from 'react';


const CategoryLink = ({ name, selected = false }) => {
    var className = "results-nav__category";
    if (selected) {
        className += " results-nav__category--active";
    }
    return (
        <a className={ className }>
            { name }
        </a>
    );
};

const Section = ({ mode, section, categories }) => {
    const links = categories.map(category => <CategoryLink key={ category.category.slug } { ...category.category } />);

    return (
        <>
            <div className="results-nav__label">{ section.round.label } - { mode.name }</div>
            { links }
        </>
    );
};

const ResultsNav = ({ sections, mode }) => {
    const blocks = sections.map(section => <Section mode={ mode } { ...section } key={ section.section.round.label } />);

    return (
        <div className="results-nav">
            <CategoryLink name="Show all" selected />
            { blocks }
        </div>
    );
};

export default ResultsNav;
