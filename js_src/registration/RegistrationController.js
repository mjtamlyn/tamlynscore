import React, { useState } from 'react';

import RegistrationFilter from './RegistrationFilter';
import RegistrationTargetList from './RegistrationTargetList';

import textMatcher from '../utils/textMatcher';

const RegistrationController = ({ targetList }) => {
    const [filterState, setFilterState] = useState({
        showRegistered: true,
        showQr: false,
        filterText: "",
    });
    const setFilter = (type, value) => {
        const newState = { ...filterState };
        newState[type] = value;
        setFilterState(newState);
    };

    const filterSet = !filterState.showRegistered | filterState.filterText.length;

    // Annotate session with stats, and mark which archers should be hidden
    targetList.forEach(session => {
        const letters = ['A', 'B' , 'C', 'D', 'E', 'F', 'G'];
        const lettersUsed = letters.slice(0, session.archersPerBoss);

        var totalEntries = 0;
        var presentCount = 0;
        var displayCount = 0;
        session.targetList.forEach(boss => {
            lettersUsed.forEach((letter) => {
                const archer = boss.archers[letter];
                if (archer) {
                    totalEntries += 1;
                    if (archer.present) {
                        presentCount += 1;
                    }

                    archer.filteredOut = false;
                    displayCount += 1;
                    if (archer.present && !filterState.showRegistered) {
                        archer.filteredOut = true;
                        displayCount -= 1;
                    } else if (filterState.filterText) {
                        if (!textMatcher(filterState.filterText, archer.searchtext)) {
                            archer.filteredOut = true;
                            displayCount -= 1;
                        }
                    }
                }
            });
        });

        session.presentCount = presentCount;
        session.totalEntries = totalEntries;
        session.percentage = totalEntries ? 100 * presentCount / totalEntries : 0;
        session.displayCount = displayCount;
    });

    return <>
        <RegistrationFilter sessions={ targetList } filterState={ filterState } setFilter={ setFilter } />
        <RegistrationTargetList targetList={ targetList } filtered={ filterSet } />
    </>;
};

export default RegistrationController;
