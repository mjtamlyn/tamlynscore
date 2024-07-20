import { useEffect, useRef } from 'react';
import { useImmerReducer } from 'use-immer';


const reducer = (state, action) => {
    switch (action.type) {
        case 'addAction':
            state.queue.push({ requestId: action.requestId, complete: false, inProgress: false, ...action.action });
            state.status = 'pending';
            return;
        case 'startRequest':
            action.requestIds.forEach(requestId => {
                state.queue.find(a => a.requestId === requestId).inProgress = true;
            });
            state.status = 'sending';
            return;
        case 'requestFailed':
            action.requestIds.forEach(requestId => {
                state.queue.find(a => a.requestId === requestId).inProgress = false;
            });
            state.status = 'retry';
            state.delay += 1000;
            return;
        case 'giveUp':
            console.log(action);
            action.requestIds.forEach(requestId => {
                state.queue.find(a => a.requestId === requestId).inProgress = false;
            });
            state.status = 'error';
            state.error = action.error;
            return;
        case 'retry':
            // Don't change the queue items here so it can retry with additional data if needed
            state.status = 'pending';
            return;
        case 'completeRequest':
            action.requestIds.forEach(requestId => {
                state.queue.find(a => a.requestId === requestId).inProgress = false;
                state.queue.find(a => a.requestId === requestId).complete = true;
            });
            // Reset the retry delay
            state.delay = 1000;
            state.status = 'ok';
            return;
        default:
            throw Error('useActionQueue: Unknown action: ' + action.type);
    }
};


const useActionQueue = (api) => {
    const [{ queue, status, error, delay }, dispatch] = useImmerReducer(reducer, { queue: [], status: 'ok', delay: 1000 });
    const requestId = useRef(0);

    useEffect(() => {
        if (!queue.length) return;
        if (!queue.find(a => !a.complete)) return;

        // Do nothing when there's an error, wait for a retry action to unset this.
        if (status === 'error' || status === 'retry') return;

        // If any actions are currently in progress, then don't start a new request
        if (queue.find(a => a.inProgress)) return;
        dispatch({ type: 'startRequest', requestIds: queue.filter(a => !a.complete).map(a => a.requestId) });
        const actions = queue.filter(a => !a.complete).map(a => { return { action: a.type, ...a.params } });
        fetch(api, {
            method: 'POST',
            credentials: 'same-origin',
            body: JSON.stringify({ actions }),
        }).then((response) => {
            if (response.status !== 200) {
                // TODO: This kind of error should display differently, not trigger the below .catch()
                throw Error('Incorrect response code');
            }
            console.log('Data saved!');
            dispatch({ type: 'completeRequest', requestIds: queue.map(a => a.requestId) });
        }).catch((e) => {
            if (delay >= 3000) {
                console.error('Giving up retrying');
                dispatch({ type: 'giveUp', requestIds: queue.map(a => a.requestId), error: e });
                return;
            }
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
        status,
        error,
    };
};

export default useActionQueue;
