import React from 'react';

import { useMutation, useQueryClient } from '@tanstack/react-query';

import ArcherPills from '../utils/ArcherPills';


const EquipmentInspection = ({ targetList, targetListApi }) => {
    const queryClient = useQueryClient();
    const mutation = useMutation({
        mutationFn: (data) => {
            return fetch(targetListApi, {
                method: 'POST',
                credentials: 'same-origin',
                body: JSON.stringify({ actions: [{
                    'action': 'KITINSPECTION',
                    ...data,
                }]}),
            });
        },
        onMutate: async ({ id, kitInspected }, context) => {
            await context.client.cancelQueries({ queryKey: ['targetList'] })
            const previous = context.client.getQueryData(['targetList'])
            context.client.setQueryData(['targetList'], (old) => {
                old.targetList.forEach(session => {
                    session.targetList.forEach(boss => {
                        Object.entries(boss.archers).forEach(([_, archer]) => {
                            if (archer?.id === id) {
                                archer.kitInspected = kitInspected;
                            }
                        });
                    });
                });
                return old;
            });
            return { previous };
        },
        onError: (err, variables, onMutateResult, context) => {
            context.client.setQueryData(['targetList'], onMutateResult.previous);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['targetList'] });
        },
    });

    const sessions = targetList.map(session => {
        const rows = [];
        const letters = ['A', 'B' , 'C', 'D', 'E', 'F', 'G'];
        const lettersUsed = letters.slice(0, session.archersPerBoss);

        session.targetList.forEach(boss => {
            lettersUsed.forEach((letter, i) => {
                const archer = boss.archers[letter];
                let bossEnd = false;
                if ((i + 1) === session.archersPerBoss) {
                    bossEnd = true;
                }
                if (archer) {
                    rows.push(
                        <tr
                                className={ "archer" + (archer.kitInspected ? " kit-inspected" : "") + (bossEnd ? " boss-end" : "") }
                                key={ `${boss.number}${letter}` }
                        >
                            <td>{ boss.number }{ letter }</td>
                            <td>
                                <div className="archer-name">
                                    <strong>{ archer.name }</strong> <small>{ archer.agbNumber }</small>
                                </div>
                                <div className="archer-category">
                                    <ArcherPills categories={ archer.categories } />
                                </div>
                            </td>
                            <td>
                                { archer.present ? "✅" : "❌" }
                            </td>
                            <td className="oneline">
                                { archer.kitInspected ? "✅" : "❌" }
                                &nbsp;
                                { archer.kitInspected
                                    ? <a className="btn btn-small btn-subtle" onClick={ () => mutation.mutate({ id: archer.id, kitInspected: false }) }>Undo</a>
                                    : <a className="btn btn-small" onClick={ () => mutation.mutate({ id: archer.id, kitInspected: true }) }>Done!</a>
                                }
                            </td>
                        </tr>
                    );
                } else {
                    let blocked = false;
                    if (session.archersPerBoss === 4) {
                        const alternateLetters = {'A': 'C', 'C': 'A', 'B': 'D', 'D': 'B'};
                        if (boss.archers[alternateLetters[letter]]?.stayOnLine) {
                            blocked = true;
                        }
                    }
                    rows.push(
                        <tr className="archer kit-inspected" key={ `${boss.number}${letter}` }>
                            <td>{ boss.number }{ letter }</td>
                            <td>{ blocked ? <strong><em>SPACE RESERVED</em></strong> : null }</td>
                            <td></td>
                            <td></td>
                        </tr>
                    );
                }
            });
        });
        return (
            <div className="registration-board" key={ session.id }>
                <h3>{ session.sessionTime }</h3>
                <table className="table">
                    <thead>
                        <tr>
                            <th>T.</th>
                            <th>Archer</th>
                            <th>Here</th>
                            <th>Kit</th>
                        </tr>
                    </thead>
                    <tbody>
                        { rows }
                    </tbody>
                </table>
            </div>
        );
    });

    return <>
        { sessions }
    </>;
};

export default EquipmentInspection;
