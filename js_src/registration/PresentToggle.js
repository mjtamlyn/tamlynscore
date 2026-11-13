import React, { useContext } from 'react';

import { useMutation, useQueryClient } from '@tanstack/react-query';

import { ApiContext } from '../context/ApiContext';


const PresentToggle = ({ archerId, present }) => {
    const targetListApi = useContext(ApiContext).targetList;
    const queryClient = useQueryClient();
    const mutation = useMutation({
        mutationFn: (data) => {
            return fetch(targetListApi, {
                method: 'POST',
                credentials: 'same-origin',
                body: JSON.stringify({ actions: [{
                    'action': 'PRESENT',
                    ...data,
                }]}),
            });
        },
        // TODO: This optimistic update doesn't work properly, I think it's
        // something to do with the component nesting? It's finding the record
        // properly, but it isn't triggering a re-render. The Judging Equipment
        // one is much "flatter" heirarchy, which may explain it?
        //
        // onMutate: async ({ id, present }, context) => {
        //     await context.client.cancelQueries({ queryKey: ['targetList'] })
        //     const previous = context.client.getQueryData(['targetList'])
        //     context.client.setQueryData(['targetList'], (old) => {
        //         old.targetList.forEach(session => {
        //             session.targetList.forEach(boss => {
        //                 Object.entries(boss.archers).forEach(([_, archer]) => {
        //                     if (archer?.id === id) {
        //                         archer.present = present;
        //                     }
        //                 });
        //             });
        //         });
        //         return old;
        //     });
        //     return { previous };
        // },
        // onError: (err, variables, onMutateResult, context) => {
        //     context.client.setQueryData(['targetList'], onMutateResult.previous);
        // },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['targetList'] });
        },
    });

    if (present) {
        return <a className="btn btn-small btn-subtle" onClick={ () => mutation.mutate({ id: archerId, present: false }) }>Remove</a>;
    } else {
        return <a className="btn btn-small" onClick={ () => mutation.mutate({ id: archerId, present: true }) }>Register</a>;
    }
};

export default PresentToggle;
