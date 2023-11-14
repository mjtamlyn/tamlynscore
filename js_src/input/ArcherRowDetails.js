import React from 'react';

import Pill from '../utils/Pill';

const ArcherRowDetails = ({ score }) => {
    return (
        <>
            <div className="archers__target">{ score.target }</div>
            <div className="archers__name">{ score.name }</div>
            <div className="archers__categories">
                <Pill type="bowstyle" value={ score.categories.bowstyle }/ >
                &nbsp;
                <Pill type="gender" value={ score.categories.gender }/ >
            </div>
        </>
    )
};

export default ArcherRowDetails;
