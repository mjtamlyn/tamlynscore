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
    const lastBossNumber = bosses.size ? Array.from(bosses.keys()).pop() : 0;
    const lookup = {};
    letters.forEach(letter => {
        lookup[letter] = null;
    });
    bosses.set(lastBossNumber + 1, lookup);
};

const addStartBoss = (bosses, letters) => {
    const firstBossNumber = bosses.keys().next().value;

    const oldBosses = Array.from(bosses.entries());
    bosses.clear()

    const lookup = {};
    letters.forEach(letter => {
        lookup[letter] = null;
    });
    bosses.set(firstBossNumber - 1, lookup);
    oldBosses.forEach(([num, lkp]) => bosses.set(num, lkp));
};

const insertBossAfter = (bosses, number, letters) => {
    const oldBosses = Array.from(bosses.entries());
    bosses.clear()
    oldBosses.forEach(([num, lkp]) => {
        if (num > number) {
            num++;
            for (const [_, archer] of Object.entries(lkp)) {
                if (archer) {
                    archer.boss++;
                }
            }
        }
        bosses.set(num, lkp);

        if (num === number) {
            const lookup = {};
            letters.forEach(letter => {
                lookup[letter] = null;
            });
            bosses.set(number + 1, lookup);
        }
    });
};

const removeBoss = (bosses, number) => {
    bosses.delete(number);

    const oldBosses = Array.from(bosses.entries());
    bosses.clear()
    oldBosses.forEach(([num, lkp]) => {
        if (num > number) {
            num--;
            for (const [_, archer] of Object.entries(lkp)) {
                if (archer) {
                    archer.boss--;
                }
            }
        }
        bosses.set(num, lkp);
    });
};

const setAllocation = (bosses, unallocatedEntries, archerId, number, target) => {
    const archer = unallocatedEntries.get(archerId);
    archer.boss = number;
    archer.target = target;
    bosses.get(number)[target] = archer;
    unallocatedEntries.delete(archerId);
};

const deleteAllocation = (bosses, unallocatedEntries, number, target) => {
    const archer = bosses.get(number)[target];
    delete bosses.get(number)[target];
    archer.boss = null;
    archer.target = null;
    unallocatedEntries.set(archer.id, archer);
};

const targetListReducer = (targetList, action) => {
    const actionQueue = targetList.actionQueue;
    const session = targetList.sessions.get(action.sessionId);

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
            actionQueue.doAction({ type: 'SHIFTUP', params: {session: action.sessionId, number: action.boss + 1}});
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
            throw Error('TargetListContext: Unknown action: ' + action.type);
        }
    }
};

const setUpTargetList = (data) => {
    const sessions = new Map();
    data.targetList.forEach(session => {
        const bosses = new Map();
        session.targetList.forEach(boss => {
            const lookup = {};
            for (const [target, archer] of Object.entries(boss.archers)) {
                if (archer) {
                    lookup[target] = archer;
                    continue;
                }
            }
            bosses.set(boss.number, lookup);
        });
        const unallocatedEntries = new Map();
        session.unallocatedEntries.forEach(entry => unallocatedEntries.set(entry.id, entry));
        sessions.set(session.id, {
            ...session,
            bosses,
            unallocatedEntries,
        });
    });
    return {
        actionQueue: data.actionQueue,
        sessions,
    };
};

const TargetListProvider = ({ children, api, targetList: initialTargetList }) => {
    const initialState = {
        targetList: initialTargetList,
        actionQueue: useActionQueue(api),
    };
    const [targetList, dispatch] = useImmerReducer(targetListReducer, initialState, setUpTargetList);

    return (
        <TargetListContext.Provider value={ targetList }>
            <TargetListDispatchContext.Provider value={ dispatch }>
                { children }
            </TargetListDispatchContext.Provider>
        </TargetListContext.Provider>
    );
};

export { TargetListContext, TargetListDispatchContext, TargetListProvider };
