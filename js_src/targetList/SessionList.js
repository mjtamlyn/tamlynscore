import React, { useContext } from 'react';

import { CompetitionContext } from '../context/CompetitionContext';
import Pill from '../utils/Pill';

const ArcherBlock = ({ place, archer }) => {
    const competition = useContext(CompetitionContext);

    if (archer) {
        return (
            <div className="archer-block">
                <div className="name">
                    <p>
                        <span className="detail">{ place }</span>
                        <span className="name">{ archer.name }</span>
                    </p>
                </div>
                <div className="bottom">
                    <p>{ archer.club }</p>
                    <p>
                        { competition.hasNovices && archer.novice && <Pill type="novice" value={ archer.novice } /> }
                        { competition.hasNovices && archer.novice && ' ' }
                        <Pill type="bowstyle" value={ archer.bowstyle } />
                        &nbsp;
                        { competition.hasAges && archer.age && <Pill type="age" value={ archer.age } /> }
                        { competition.hasAges && archer.age && ' ' }
                        <Pill type="gender" value={ archer.gender } />
                    </p>
                </div>
            </div>
        );
    }
    return (
        <div className="archer-block">
            <div className="name">
                <p>
                    <span className="detail">{ place }</span>
                </p>
            </div>
            <div className="bottom"></div>
        </div>
    );
}

const Boss = ({ number, perBoss, archers }) => {
    const letters = ['A', 'B' , 'C', 'D', 'E', 'F', 'G'];
    const lettersUsed = letters.slice(0, perBoss);

    const blocks = lettersUsed.map(letter => <ArcherBlock place={ `${number}${letter}` } archer={ archers[letter] } key={ letter } />);

    return (
        <div className="boss">
            { blocks }
        </div>
    );
}

const SessionList = ({ targets, perBoss }) => {
    const bosses = targets.map(boss => <Boss number={ boss.number } perBoss={ perBoss } archers={ boss.archers } key={ boss.number } />);
    return bosses;
}

export default SessionList;
