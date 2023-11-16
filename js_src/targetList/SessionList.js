import React, { useState, useContext } from 'react';

import { TargetListDispatchContext } from '../context/TargetListContext';
import ArcherPills from '../utils/ArcherPills';
import ArcherSelector from './ArcherSelector';

const EmptyArcherBlock = ({ place, editMode, unallocatedEntries, setAllocation }) => {
    const [selectOpen, setSelectOpen] = useState(false);

    return (
        <div className="archer-block">
            <div className="name">
                <span className="detail">{ place }</span>
                { editMode && <a className="select" onClick={ () => setSelectOpen(!selectOpen) }>Select…</a> }
            </div>
            { selectOpen && <ArcherSelector archers={ unallocatedEntries } close={ () => setSelectOpen(false) } onSelect={ setAllocation } /> }
            <div className="bottom"></div>
        </div>
    );
};

const ArcherBlock = ({ place, archer, editMode, deleteAllocation }) => {
    return (
        <div className="archer-block">
            <div className="name">
                { place && <span className="detail">{ place }</span> }
                <span>
                    { archer.name }
                    { editMode && <span className="actions">
                        <a className="delete action-button" onClick={ deleteAllocation }></a>
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
    const dispatch = useContext(TargetListDispatchContext);
    const bosses = session.bosses;
    const letters = ['A', 'B' , 'C', 'D', 'E', 'F', 'G'];
    const lettersUsed = letters.slice(0, session.archersPerBoss);
    const lastBossNumber = session.bosses.length ? session.bosses[session.bosses.length - 1].number : null;

    const displayBosses = bosses.map(boss => {
        let bossIsEmpty = true;
        const blocks = lettersUsed.map(letter => {
            if (boss.lookup[letter]) {
                bossIsEmpty = false;
                const deleteAllocation = () => {
                    boss.lookup[letter].deleteAllocation();
                    setBosses([...session.bosses]);
                };
                return (
                    <ArcherBlock
                        key={ letter }
                        place={ `${boss.number}${letter}` }
                        archer={ boss.lookup[letter] }
                        editMode={ editMode }
                        deleteAllocation={ () => dispatch({ type: 'deleteAllocation', sessionId: session.id, boss: boss.number, letter, archerId: boss.lookup[letter].id }) }
                    />
                );
            }
            return (
                <EmptyArcherBlock
                    place={ `${boss.number}${letter}` }
                    key={ letter }
                    editMode={ editMode }
                    unallocatedEntries={ session.unallocatedEntries }
                    setAllocation={ (archer) => dispatch({ type: 'setAllocation', sessionId: session.id, boss: boss.number, letter, archerId: archer.id }) }
                />
            );
        });

        return (
            <div key={ boss.number }>
                { editMode && bossIsEmpty && <a className="target-list__btn btn delete" onClick={ () => dispatch({ type: 'removeBoss', sessionId: session.id, boss: boss.number }) }>Remove empty target</a> }
                <div className="boss">
                    { blocks }
                </div>
                { editMode && boss.number !== lastBossNumber && <a className="target-list__btn btn insert" onClick={ () => dispatch({ type: 'insertBossAfter', sessionId: session.id, boss: boss.number }) }>Insert target</a> }
            </div >
        );
    });

    const canStartAdd = bosses.length ? bosses[0].number > 1 : null;

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
            { editMode && canStartAdd && <a className="target-list__btn btn add" onClick={ () => dispatch({ type: 'addStartBoss', sessionId: session.id }) }>Add target</a> }
            { editMode && !canStartAdd && (bosses.length || null) && <a className="target-list__btn btn insert" onClick={ () => dispatch({ type: 'insertBossAfter', sessionId: session.id, boss: 0 }) }>Insert target</a> }
            { displayBosses }
            { editMode && <a className="target-list__btn btn add" onClick={ () => dispatch({ type: 'addBoss', sessionId: session.id }) }>Add target</a> }
            { unallocated }
        </>
    );
}

export default SessionList;
