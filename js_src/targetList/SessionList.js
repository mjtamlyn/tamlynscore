import React, { useState, useContext } from 'react';

import { CompetitionContext } from '../context/CompetitionContext';
import Pill from '../utils/Pill';

const ArcherBlock = ({ place, archer, editMode, deleteAllocation }) => {
    const competition = useContext(CompetitionContext);

    if (archer) {
        const deleteHandler = (e) => {
            e.preventDefault();
            deleteAllocation();
        };
        return (
            <div className="archer-block">
                <div className="name">
                    { place && <span className="detail">{ place }</span> }
                    <span>
                        { archer.name }
                        { editMode && <span className="actions">
                            <a className="delete action-button" onClick={ deleteHandler }></a>
                        </span> }
                    </span>
                </div>
                <div className="bottom">
                    <p>{ archer.club }</p>
                    <p>
                        { competition.hasNovices && archer.categories.novice && <Pill type="novice" value={ archer.categories.novice } /> }
                        { competition.hasNovices && archer.categories.novice && ' ' }
                        <Pill type="bowstyle" value={ archer.categories.bowstyle } />
                        &nbsp;
                        { competition.hasAges && archer.categories.age && <Pill type="age" value={ archer.categories.age } /> }
                        { competition.hasAges && archer.categories.age && ' ' }
                        <Pill type="gender" value={ archer.categories.gender } />
                    </p>
                </div>
            </div>
        );
    }
    return (
        <div className="archer-block">
            <div className="name">
                <span className="detail">{ place }</span>
                { editMode && <span>Select…</span> }
            </div>
            <div className="bottom"></div>
        </div>
    );
}

const SessionList = ({ session, editMode }) => {
    const [bosses, setBosses] = useState(session.bosses);
    const letters = ['A', 'B' , 'C', 'D', 'E', 'F', 'G'];
    const lettersUsed = letters.slice(0, session.archersPerBoss);

    const displayBosses = bosses.map(boss => {
        const blocks = lettersUsed.map(letter => {
            const deleteAllocation = () => {
                boss.lookup[letter].deleteAllocation();
                setBosses([...session.bosses]);
            };
            return (
                <ArcherBlock place={ `${boss.number}${letter}` } archer={ boss.lookup[letter] } key={ letter } editMode={ editMode } deleteAllocation={ deleteAllocation } />
            );
        });

        return (
            <div className="boss" key={ boss.number }>
                { blocks }
            </div>
        );
    });

    const addBossHandler = (e) => {
        e.preventDefault();
        session.addBoss(lettersUsed);
        setBosses([...session.bosses]);
    }

    let unallocated = null;
    if (session.unallocatedEntries.length && editMode) {
        const unallocatedBlocks = session.unallocatedEntries.map(archer => {
            console.log(archer);
            return <ArcherBlock archer={ archer } editMode={ false } key={ archer.id } />
        });
        unallocated = (
            <div className="unallocated">
                <h4>Unallocated entries</h4>
                { unallocatedBlocks }
            </div>
        );
    }

    return (
        <>
            { displayBosses }
            { editMode && <a className="btn add" onClick={ addBossHandler }>Add target</a> }
            { unallocated }
        </>
    );
}

export default SessionList;
