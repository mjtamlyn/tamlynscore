import React, { createContext, useEffect } from 'react';
import { useImmerReducer } from 'use-immer';

import useActionQueue from '../utils/useActionQueue';

const TargetListContext = createContext(null);
const TargetListDispatchContext = createContext(null);

const getLetters = (session) => {
    const letters = ['A', 'B' , 'C', 'D', 'E', 'F', 'G'];
    return letters.slice(0, session.archersPerBoss);
};

const addBoss = (bosses, letters) => {
    const lastBossNumber = bosses.length ? bosses[bosses.length - 1].number : 0;
    const lookup = {};
    letters.forEach(letter => {
        lookup[letter] = null;
    });
    bosses.push({
        number: lastBossNumber + 1,
        lookup: lookup,
    });
};

const addStartBoss = (bosses, letters) => {
    const firstBossNumber = bosses[0].number;
    const lookup = {};
    letters.forEach(letter => {
        lookup[letter] = null;
    });
    bosses.insert(0, {
        number: firstBossNumber - 1,
        lookup: lookup,
    });
};

const insertBossAfter = (bosses, number, letters) => {
    const index = bosses.findIndex(boss => boss.number === number);
    const lookup = {};
    letters.forEach(letter => {
        lookup[letter] = null;
    });
    bosses.filter(boss => boss.number > number).forEach(boss => {
        boss.number++;
        for (const [_, archer] of Object.entries(boss.lookup)) {
            archer.boss++;
        }
    });
    bosses.splice(index + 1, 0, {
        number: number + 1,
        lookup: lookup,
    });
};

const removeBoss = (bosses, number) => {
    bosses.filter(boss => boss.number > number).forEach(boss => {
        boss.number--;
        for (const [_, archer] of Object.entries(boss.lookup)) {
            archer.boss--;
        }
    });
    const index = bosses.findIndex(boss => boss.number === number);
    bosses.splice(index, 1);
};

const setAllocation = (bosses, unallocatedEntries, archerId, number, target) => {
    const index = unallocatedEntries.findIndex(archer => archer.id === archerId);
    const archer = unallocatedEntries[index];
    archer.boss = number;
    archer.target = target;
    bosses.find(boss => boss.number === number).lookup[target] = archer;
    unallocatedEntries.splice(index, 1);
};

const deleteAllocation = (bosses, unallocatedEntries, number, target) => {
    const archer = bosses.find(boss => boss.number === number).lookup[target];
    delete bosses.find(boss => boss.number === number).lookup[target];
    archer.boss = null;
    archer.target = null;
    unallocatedEntries.push(archer);
};

const targetListReducer = (targetList, action) => {
    let session = null;
    const actionQueue = targetList.actionQueue;
    if (action.sessionId) {
        session = targetList.sessions.find(session => session.id = action.sessionId);
    }

    switch(action.type) {
        case 'addBoss': {
            addBoss(session.bosses, getLetters(session));
            return;
        }
        case 'addStartBoss': {
            addStartBoss(session.bosses, getLetters(session));
            return;
        }
        case 'insertBossAfter': {
            insertBossAfter(session.bosses, action.boss, getLetters(session));
            actionQueue.doAction({ type: 'SHIFTUP', params: {session: action.sessionId, number: action.boss}});
            return;
        }
        case 'removeBoss': {
            removeBoss(session.bosses, action.boss);
            actionQueue.doAction({ type: 'SHIFTDOWN', params: {session: action.sessionId, number: action.boss}});
            return;
        }
        case 'setAllocation': {
            setAllocation(session.bosses, session.unallocatedEntries, action.archerId, action.boss, action.letter);
            actionQueue.doAction({ type: 'SET', params: {id: action.archerId, value: { boss: action.boss, target:action.letter }}});
            return;
        }
        case 'deleteAllocation': {
            deleteAllocation(session.bosses, session.unallocatedEntries, action.boss, action.letter);
            actionQueue.doAction({ type: 'DELETE', params: {id: action.archerId}});
            return;
        }
        default: {
            throw Error('Unknown action: ' + action.type);
        }
    }
};

const setUpTargetList = (data) => {
    return {
        actionQueue: data.actionQueue,
        sessions: data.map(session => {
            session.bosses = session.targetList.map(boss => {
                const lookup = {};
                for (const [target, archer] of Object.entries(boss.archers)) {
                    if (archer) {
                        lookup[target] = archer;
                        continue;
                    }
                }
                return {
                    number: boss.number,
                    lookup
                };
            });
            return session;
        }),
    };
};

const TargetListProvider = ({ children, api, targetList: initialTargetList }) => {
    initialTargetList.actionQueue = useActionQueue(api);
    const [targetList, dispatch] = useImmerReducer(targetListReducer, initialTargetList, setUpTargetList);

    return (
        <TargetListContext.Provider value={ targetList }>
            <TargetListDispatchContext.Provider value={ dispatch }>
                { children }
            </TargetListDispatchContext.Provider>
        </TargetListContext.Provider>
    );
};

export { TargetListContext, TargetListDispatchContext, TargetListProvider };
