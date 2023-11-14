import React from 'react';

import ArcherPills from '../utils/ArcherPills';

const ArcherRowDetails = ({ score }) => {
    return (
        <>
            <div className="archers__target">{ score.target }</div>
            <div className="archers__name">{ score.name }</div>
            <div className="archers__categories">
                <ArcherPills categories={ score.categories } />
            </div>
        </>
    )
};

export default ArcherRowDetails;
