import { useEffect } from 'react';
import { useImmer } from 'use-immer';


let requestId = 0;

const useActionQueue = (api) => {
    const [queue, setQueue] = useImmer([]);

    useEffect(() => {
        if (!queue.length) return;

        // only do one at a time for safety for now
        const action = queue[0];
        if (action.inProgress) return;
        setQueue((current) => {
            current.find(a => a.requestId === action.requestId).inProgress = true;
        });
        const data = { action: action.type, ...action.params };
        fetch(api, {
            method: 'POST',
            credentials: 'same-origin',
            body: JSON.stringify(data),
        }).then((response) => {
            if (response.status !== 200) {
                throw Error('Incorrect response code');
            }
            setQueue((current) => {
                const index = current.findIndex(a => a.requestId === action.requestId);
                current.splice(index, 1);
            });
        }).catch(() => {
            throw Error('something went wrong');
        });
    }, [queue]);

    return {
        doAction: (action) => {
            setQueue((current) => {
                current.push({ requestId: requestId++, ...action });
            });
        },
    };
};

export default useActionQueue;
