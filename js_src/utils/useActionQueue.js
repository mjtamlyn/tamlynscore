import { useEffect, useRef } from 'react';
import { useImmerReducer } from 'use-immer';


const reducer = (state, action) => {
    switch (action.type) {
        case 'addAction':
            state.queue.push({ requestId: action.requestId, ...action.action });
            return;
        case 'startRequest':
            action.requestIds.forEach(requestId => {
                state.queue.find(a => a.requestId === requestId).inProgress = true;
            });
            return;
        case 'requestFailed':
            action.requestIds.forEach(requestId => {
                state.queue.find(a => a.requestId === requestId).inProgress = false;
            });
            state.status = 'error';
            state.delay += 1000;
            return;
        case 'retry':
            // Don't change the queue items here so it can retry with additional data if needed
            state.status = 'ok';
            return;
        case 'completeRequest':
            action.requestIds.forEach(requestId => {
                const index = state.queue.findIndex(a => a.requestId === requestId);
                state.queue.splice(index, 1);
            });
            // Reset the retry delay
            state.delay = 1000;
            return;
        default:
            throw Error('useActionQueue: Unknown action: ' + action.type);
    }
};


const useActionQueue = (api) => {
    const [{ queue, status, delay }, dispatch] = useImmerReducer(reducer, { queue: [], status: 'ok', delay: 1000 });
    const requestId = useRef(0);

    useEffect(() => {
        if (!queue.length) return;

        // Do nothing when there's an error, wait for a retry action to unset this.
        if (status === 'error') return;

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
            console.log('Data saved!');
            dispatch({ type: 'completeRequest', requestIds: queue.map(a => a.requestId) });
        }).catch((e) => {
            // TODO: if more than 10 retries have been attempted then we should display something
            console.error('Save failed, will retry after', delay);
            dispatch({ type: 'requestFailed', requestIds: queue.map(a => a.requestId) });
            setTimeout(() => {
                console.log('Retry initiated after', delay);
                dispatch({ type: 'retry' });
            }, delay);
        });
    }, [queue, status]);

    return {
        doAction: (action) => {
            requestId.current = requestId.current + 1
            dispatch({ type: 'addAction', requestId: requestId.current, action });
        },
    };
};

export default useActionQueue;
