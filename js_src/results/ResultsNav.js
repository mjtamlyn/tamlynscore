import React from 'react';


const CategoryLink = ({ name, resultsetId, selectedCategory, setSelectedCategory }) => {
    var className = "results-nav__category";
    if (selectedCategory === resultsetId) {
        className += " results-nav__category--active";
    }
    return (
        <a className={ className } onClick={ () => setSelectedCategory(resultsetId) }>
            { name }
        </a>
    );
};

const ResultsNav = ({ sections, mode, selectedCategory, setSelectedCategory }) => {
    const blocks = [];

    sections.forEach(({ section, categories }) => {
        blocks.push(<div key={ section.round.codename } className="results-nav__label">{ section.round.label } - { mode.name }</div>);
        categories.forEach(({ category }) => {
            const resultsetId = `${section.round.codename}-${category.slug}`;
            blocks.push(<CategoryLink key={ resultsetId } resultsetId={ resultsetId } selectedCategory={ selectedCategory } setSelectedCategory={ setSelectedCategory } { ...category } />);
        });
    });

    return (
        <div className="results-nav">
            <CategoryLink name="Show all" selectedCategory={ selectedCategory } resultsetId={ null } setSelectedCategory={ setSelectedCategory } />
            { blocks }
        </div>
    );
};

export default ResultsNav;
