import React, { createContext, useEffect } from 'react';
import { useImmerReducer } from 'use-immer';

const TargetListContext = createContext(null);
const TargetListDispatchContext = createContext(null);

let requestId = 0;

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
            targetList.actionsToSave.push({ type: 'SHIFTUP', requestId: requestId++, params: {session: action.sessionId, number: action.boss}});
            return;
        }
        case 'removeBoss': {
            removeBoss(session.bosses, action.boss);
            targetList.actionsToSave.push({ type: 'SHIFTDOWN', requestId: requestId++, params: {session: action.sessionId, number: action.boss}});
            return;
        }
        case 'setAllocation': {
            setAllocation(session.bosses, session.unallocatedEntries, action.archerId, action.boss, action.letter);
            targetList.actionsToSave.push({ type: 'SET', requestId: requestId++, params: {id: action.archerId, value: { boss: action.boss, target:action.letter }}});
            return;
        }
        case 'deleteAllocation': {
            deleteAllocation(session.bosses, session.unallocatedEntries, action.boss, action.letter);
            targetList.actionsToSave.push({ type: 'DELETE', requestId: requestId++, params: {id: action.archerId}});
            return;
        }
        case 'startRequest': {
            targetList.actionsToSave.find(a => a.requestId === action.requestId).inProgress = true;
            return;
        }
        case 'clearRequest': {
            const index = targetList.actionsToSave.findIndex(a => a.requestId === action.requestId);
            targetList.actionsToSave.splice(index, 1);
            return;
        }
        default: {
            throw Error('Unknown action: ' + action.type);
        }
    }
};

const setUpTargetList = (data) => {
    return {
        actionsToSave: [],
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
    const [targetList, dispatch] = useImmerReducer(targetListReducer, initialTargetList, setUpTargetList);

    useEffect(() => {
        if (!targetList.actionsToSave.length) return;

        // only do one at a time for safety for now
        const action = targetList.actionsToSave[0];
        if (action.inProgress) return;
        dispatch({ type: 'startRequest', requestId: action.requestId });
        const data = { action: action.type, ...action.params };
        fetch(api, {
            method: 'POST',
            credentials: 'same-origin',
            body: JSON.stringify(data),
        }).then((response) => {
            dispatch({ type: 'clearRequest', requestId: action.requestId });
            if (response.status !== 200) {
                throw Error('Incorrect response code');
            }
        }).catch(() => {
            throw Error('something went wrong');
        });
    }, [targetList.actionsToSave]);

    return (
        <TargetListContext.Provider value={ targetList }>
            <TargetListDispatchContext.Provider value={ dispatch }>
                { children }
            </TargetListDispatchContext.Provider>
        </TargetListContext.Provider>
    );
};

export { TargetListContext, TargetListDispatchContext, TargetListProvider };
