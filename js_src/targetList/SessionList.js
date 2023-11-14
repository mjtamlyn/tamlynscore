import React, { useState, useContext, useEffect, useRef } from 'react';

import useMousetrap from 'react-hook-mousetrap';

import { CompetitionContext } from '../context/CompetitionContext';
import Pill from '../utils/Pill';

const ArcherSelector = ({ archers, onSelect, close, emptyLabel="Select…" }) => {
    const ref = useRef(null);
    const closeHandler = (e) => {
        if (ref && !ref.current.closest('.archer-block').contains(e.target)) {
            close();
        }
    };
    useEffect(() => {
        document.body.addEventListener('click', closeHandler);
        return () => document.body.removeEventListener('click', closeHandler);
    });
    useMousetrap('esc', close);

    const archerList = archers.map(archer => {
        const clickHandler = (e) =>{
            e.preventDefault();
            onSelect(archer);
            close();
        }
        return <li key={ archer.id } onClick={ clickHandler }>{ archer.name }</li>;
    });

    return (
        <div className="archer-selector" ref={ ref }>
            <ul>
                <li>{ emptyLabel }</li>
                { archerList }
            </ul>
        </div>
    );
};

const EmptyArcherBlock = ({ place, editMode, unallocatedEntries, setAllocation }) => {
    const [selectOpen, setSelectOpen] = useState(false);

    const selectHandler = (e) => {
        e.preventDefault();
        setSelectOpen(!selectOpen);
    };
    const close = () => {
        setSelectOpen(false);
    };

    return (
        <div className="archer-block">
            <div className="name" onClick={ selectHandler }>
                <span className="detail">{ place }</span>
                { editMode && <span>Select…</span> }
            </div>
            { selectOpen && <ArcherSelector archers={ unallocatedEntries } close={ close } onSelect={ setAllocation } /> }
            <div className="bottom"></div>
        </div>
    );
};

const ArcherBlock = ({ place, archer, editMode, deleteAllocation }) => {
    const competition = useContext(CompetitionContext);

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

const SessionList = ({ session, editMode }) => {
    const [bosses, setBosses] = useState(session.bosses);
    const letters = ['A', 'B' , 'C', 'D', 'E', 'F', 'G'];
    const lettersUsed = letters.slice(0, session.archersPerBoss);

    const displayBosses = bosses.map(boss => {
        const blocks = lettersUsed.map(letter => {
            if (boss.lookup[letter]) {
                const deleteAllocation = () => {
                    boss.lookup[letter].deleteAllocation();
                    setBosses([...session.bosses]);
                };
                return (
                    <ArcherBlock place={ `${boss.number}${letter}` } archer={ boss.lookup[letter] } key={ letter } editMode={ editMode } deleteAllocation={ deleteAllocation } />
                );
            }
            const setAllocation = (archer) => {
                archer.setAllocation({ boss: boss.number, target: letter });
                setBosses([...session.bosses]);
            }
            return (
                <EmptyArcherBlock place={ `${boss.number}${letter}` } key={ letter } editMode={ editMode } unallocatedEntries={ session.unallocatedEntries } setAllocation={ setAllocation } />
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
    const canStartAdd = bosses[0].number > 1;
    const addStartBossHandler = (e) => {
        e.preventDefault();
        session.addStartBoss(lettersUsed);
        setBosses([...session.bosses]);
    }

    let unallocated = null;
    if (session.unallocatedEntries.length && editMode) {
        const unallocatedBlocks = session.unallocatedEntries.map(archer => {
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
            { editMode && canStartAdd && <a className="btn add" onClick={ addStartBossHandler }>Add target</a> }
            { displayBosses }
            { editMode && <a className="btn add" onClick={ addBossHandler }>Add target</a> }
            { unallocated }
        </>
    );
}

export default SessionList;
