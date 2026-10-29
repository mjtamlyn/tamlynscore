import React from 'react';

import ArcherPills from '../utils/ArcherPills';


const EquipmentInspection = ({ targetList }) => {

    const sessions = targetList.map(session => {
        const rows = [];
        const letters = ['A', 'B' , 'C', 'D', 'E', 'F', 'G'];
        const lettersUsed = letters.slice(0, session.archersPerBoss);

        session.targetList.forEach(boss => {
            lettersUsed.forEach(letter => {
                const archer = boss.archers[letter];
                if (archer) {
                    rows.push(
                        <tr className={ "archer" + (archer.kitInspected ? " kit-inspected" : "") } key={ `${boss.number}${letter}` }>
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
                                    ? <a className="btn btn-small btn-subtle">Undo</a>
                                    : <a className="btn btn-small">Done!</a>
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
            <div className="registration-board">
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
