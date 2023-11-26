import { useEffect, useRef } from 'react';
import { useImmerReducer } from 'use-immer';


const reducer = (queue, action) => {
    switch (action.type) {
        case 'addAction':
            queue.push({ requestId: action.requestId, ...action.action });
            return;
        case 'startRequest':
            action.requestIds.forEach(requestId => {
                queue.find(a => a.requestId === requestId).inProgress = true;
            });
            return;
        case 'completeRequest':
            action.requestIds.forEach(requestId => {
                const index = queue.findIndex(a => a.requestId === requestId);
                queue.splice(index, 1);
            });
            return;
        case 'default':
            throw Error('useActionQueue: Unknown action: ' + action.type);
    }
};


const useActionQueue = (api) => {
    const [queue, dispatch] = useImmerReducer(reducer, []);
    const requestId = useRef(0);

    useEffect(() => {
        if (!queue.length) return;

        const firstAction = queue[0];
        // If any actions are currently in progress, then don't start a new request
        if (firstAction.inProgress) return;
        dispatch({ type: 'startRequest', requestIds: queue.map(a => a.requestId) });
        const actions = queue.map(a => { return { action: a.type, ...a.params } });
        fetch(api, {
            method: 'POST',
            credentials: 'same-origin',
            body: JSON.stringify({ actions }),
        }).then((response) => {
            if (response.status !== 200) {
                throw Error('Incorrect response code');
            }
            dispatch({ type: 'completeRequest', requestIds: queue.map(a => a.requestId) });
        }).catch(() => {
            throw Error('something went wrong');
        });
    }, [queue]);

    return {
        doAction: (action) => {
            requestId.current = requestId.current + 1
            dispatch({ type: 'addAction', requestId: requestId.current, action });
        },
    };
};

export default useActionQueue;
