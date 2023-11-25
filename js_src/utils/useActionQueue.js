import { useEffect, useRef } from 'react';
import { useImmerReducer } from 'use-immer';


const reducer = (queue, action) => {
    switch (action.type) {
        case 'addAction':
            queue.push({ requestId: action.requestId, ...action.action });
            return;
        case 'startRequest':
            queue.find(a => a.requestId === action.requestId).inProgress = true;
            return;
        case 'completeRequest':
            const index = current.findIndex(a => a.requestId === action.requestId);
            current.splice(index, 1);
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

        // only do one at a time for safety for now
        const action = queue[0];
        if (action.inProgress) return;
        dispatch({ type: 'startRequest', requestId: action.requestId });
        const data = { action: action.type, ...action.params };
        fetch(api, {
            method: 'POST',
            credentials: 'same-origin',
            body: JSON.stringify(data),
        }).then((response) => {
            if (response.status !== 200) {
                throw Error('Incorrect response code');
            }
            dispatch({ type: 'startRequest', requestId: action.requestId });
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
