import React, { useState } from 'react';

import Toggle from '../utils/Toggle';


const RegistrationFilter = ({ sessions }) => {
    const [showRegistered, setShowRegistered] = useState(true);
    const [showQr, setShowQr] = useState(false);

    // this should serve as a navigation for the top of the page
    // show the session(s), and indicate how "complete" they are
    // give a search box to filter
    // give a toggle to hide registered archers
    // give a toggle to show QR codes(?)

    const items = sessions.map(session => {
        var totalEntries = 0;
        var presentCount = 0;

        const letters = ['A', 'B' , 'C', 'D', 'E', 'F', 'G'];
        const lettersUsed = letters.slice(0, session.archersPerBoss);

        session.targetList.forEach(boss => {
            lettersUsed.forEach((letter) => {
                const archer = boss.archers[letter];
                if (archer) {
                    totalEntries += 1;
                    if (archer.present) {
                        presentCount += 1;
                    }
                }
            });
        });

        return (
            <div className="entries-filter__session" key={ session.id }>
                <div>{ session.sessionTime }</div>
                <div>
                    <span className="pill pill--percentage" data-percentage={ totalEntries ? 100 * presentCount / totalEntries : 0 }>
                        { presentCount } / { totalEntries } present
                    </span>
                </div>
            </div>
        );
    });

    return (
        <div className="entries-filter">
            <div className="entries-filter__filter">
                <input placeholder="Enter a name, club, bow type etc…" />
            </div>
            <div className="entries-filter__toggle">
                <span>Show registered?</span>
                <Toggle on={ showRegistered } setOn={ setShowRegistered } />
            </div>
            <div className="entries-filter__toggle">
                <span>Show QR codes?</span>
                <Toggle on={ showQr } setOn={ setShowQr } />
            </div>
            <div className="entries-filter__sessions">
                { items }
            </div>
        </div>
    );
};

export default RegistrationFilter;
