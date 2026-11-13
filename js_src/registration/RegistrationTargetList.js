import React from 'react';

import ArcherPills from '../utils/ArcherPills';

import PresentToggle from './PresentToggle';

const SessionTargetList = ({ session, filtered, showQr }) => {
    const rows = [];
    const letters = ['A', 'B' , 'C', 'D', 'E', 'F', 'G'];
    const lettersUsed = letters.slice(0, session.archersPerBoss);

    session.targetList.forEach(boss => {
        lettersUsed.forEach((letter, i) => {
            const archer = boss.archers[letter];
            let bossEnd = false;
            if ((i + 1) === session.archersPerBoss && !filtered) {
                // Don't bother with boss dividers when we are filtering
                bossEnd = true;
            }
            if (archer) {
                if (archer.filteredOut) {
                    return null;
                }
                rows.push(
                    <tr
                            className={ "archer" + (archer.present ? " kit-inspected" : "") + (bossEnd ? " boss-end" : "") }
                            key={ `${boss.number}${letter}` }
                    >
                        <td>{ boss.number }{ letter }</td>
                        <td>
                            <div className="archer-name">
                                <strong>{ archer.name }</strong> · <small>{ archer.agbNumber } · { archer.round }</small>
                            </div>
                            <div className="archer-category">
                                <ArcherPills categories={ archer.categories } />
                            </div>
                        </td>
                        <td>{ archer.club }</td>
                        <td className="oneline">
                            { archer.kitInspected ? "✅" : "❌" }
                        </td>
                        <td>
                            { archer.present ? "✅" : "❌" }
                            <PresentToggle archerId={ archer.id } present={ archer.present } />
                        </td>
                        { showQr && archer.qrApi && <td>
                            <img className="qr-code" src={ archer.qrApi } />
                        </td> }
                    </tr>
                );
            } else {
                if (filtered) {
                    return null;
                }

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
                        <td></td>
                        { showQr && <td></td> }
                    </tr>
                );
            }
        });
    });

    return <>
        <h3>{ session.sessionTime }</h3>
        <table className="table">
            <thead>
                <tr>
                    <th>T.</th>
                    <th>Archer</th>
                    <th>Club</th>
                    <th>Kit</th>
                    <th>Here</th>
                    { showQr && <th>QR code</th> }
                </tr>
            </thead>
            <tbody>
                { rows }
            </tbody>
        </table>
    </>;
};

const RegistrationTargetList = ({ targetList, filtered, showQr }) => {
    var anythingToRender = false;
    const sessions = targetList.map((session) => {
        if (filtered && !session.displayCount) {
            return null;
        }
        anythingToRender = true;
        return <SessionTargetList session={ session } key={ session.id } filtered={ filtered } showQr={ showQr } />;
    });

    if (!anythingToRender) {
        return <p className="entries-filter__warning">No matches found</p>;
    }

    return (
        <div className="registration-board">
            { sessions }
        </div>
    );
};

export default RegistrationTargetList;
