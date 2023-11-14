import React, { useContext } from 'react';

import { CompetitionContext } from '../context/CompetitionContext';
import Pill from '../utils/Pill';


const ArcherPills = ({ categories }) => {
    const competition = useContext(CompetitionContext);

    return (
        <>
            { competition.hasNovices && categories.novice && <Pill type="novice" value={ categories.novice } /> }
            { competition.hasNovices && categories.novice && ' ' }
            <Pill type="bowstyle" value={ categories.bowstyle } />
            &nbsp;
            { competition.hasAges && categories.age && <Pill type="age" value={ categories.age } /> }
            { competition.hasAges && categories.age && ' ' }
            <Pill type="gender" value={ categories.gender } />
        </>
    );
};

export default ArcherPills;
