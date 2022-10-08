import React from 'react';

import ArcherRow from './ArcherRow';
import EventHeader from './EventHeader';
import ScoreInput from './ScoreInput';


const TargetInput = () => {
    return (
        <div className="full-height-page">
            <EventHeader round="WA 18" endNumber={ 3 } />
            <div className="archers">
                <ArcherRow />
                <ArcherRow />
                <ArcherRow />
                <ArcherRow />
            </div>
            <ScoreInput />
        </div>
    );
};

export default TargetInput;
