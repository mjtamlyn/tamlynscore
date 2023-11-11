import React, { useContext } from 'react';

import { CompetitionContext } from '../context/CompetitionContext';
import Pill from '../utils/Pill';

const ArcherBlock = ({ place, archer, editMode }) => {
    const competition = useContext(CompetitionContext);

    if (archer) {
        return (
            <div className="archer-block">
                <div className="name">
                    <span className="detail">{ place }</span>
                    <span className="name">
                        { archer.name }
                        { editMode && <span className="actions">
                            <a className="delete action-button"></a>
                        </span> }
                    </span>
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
                <span className="detail">{ place }</span>
                { editMode && <span className="name">Select…</span> }
            </div>
            <div className="bottom"></div>
        </div>
    );
}

const Boss = ({ number, perBoss, archers, editMode }) => {
    const letters = ['A', 'B' , 'C', 'D', 'E', 'F', 'G'];
    const lettersUsed = letters.slice(0, perBoss);

    const blocks = lettersUsed.map(letter => <ArcherBlock place={ `${number}${letter}` } archer={ archers[letter] } key={ letter } editMode={ editMode } />);

    return (
        <div className="boss">
            { blocks }
        </div>
    );
}

const SessionList = ({ targets, perBoss, editMode }) => {
    const bosses = targets.map(boss => <Boss number={ boss.number } perBoss={ perBoss } archers={ boss.archers } key={ boss.number } editMode={ editMode } />);
    return bosses;
}

export default SessionList;
