import React from 'react';


const CategoryLink = ({ name }) => {
    return (
        <div className="section-selector__category">
            { name }
        </div>
    );
};

const Section = ({ mode, section, categories }) => {
    const links = categories.map(category => <CategoryLink key={ category.category.slug } { ...category.category } />);

    return (
        <div className="section-selector__section">
            <h3 className="section-selector__label">{ section.round.label } - { mode.name }</h3>
            <div className="section-selector__categories">
                { links }
            </div>
        </div>
    );
};

const SectionSelector = ({ sections, mode }) => {
    const blocks = sections.map(section => <Section mode={ mode } { ...section } key={ section.section.round.label } />);

    return (
        <div className="section-selector">
            { blocks }
        </div>
    );
};

export default SectionSelector;
