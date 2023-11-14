import React, { useState } from 'react';

import ArcherPills from '../utils/ArcherPills';
import ArcherSelector from './ArcherSelector';

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
            <div className="name">
                <span className="detail">{ place }</span>
                { editMode && <span className="select" onClick={ selectHandler }>Select…</span> }
            </div>
            { selectOpen && <ArcherSelector archers={ unallocatedEntries } close={ close } onSelect={ setAllocation } /> }
            <div className="bottom"></div>
        </div>
    );
};

const ArcherBlock = ({ place, archer, editMode, deleteAllocation }) => {
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
                <p><ArcherPills categories={ archer.categories } /></p>
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
