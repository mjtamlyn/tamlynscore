import React from 'react';

import Toggle from '../utils/Toggle';


const RegistrationFilter = ({ sessions, filterState, setFilter, hasQrs }) => {
    const items = sessions.map(session => {
        return (
            <div className="entries-filter__session" key={ session.id }>
                <div>{ session.sessionTime }</div>
                <div>
                    <span className="pill pill--percentage" data-percentage={ session.percentage }>
                        { session.presentCount } / { session.totalEntries } present
                    </span>
                </div>
            </div>
        );
    });

    return (
        <div className="entries-filter">
            <div className="entries-filter__filter">
                <input value={ filterState.filterText } onChange={ (e) => setFilter('filterText', e.target.value) } placeholder="Enter a name, club, bow type etc…" autoFocus />
            </div>
            <div className="entries-filter__toggle">
                <span>Show registered?</span>
                <Toggle on={ filterState.showRegistered } setOn={ (value) => setFilter('showRegistered', value) } />
            </div>
            { hasQrs && <div className="entries-filter__toggle">
                <span>Show QR codes?</span>
                <Toggle on={ filterState.showQr } setOn={ (value) => setFilter('showQr', value) } />
            </div> }
            <div className="entries-filter__sessions">
                { items }
            </div>
        </div>
    );
};

export default RegistrationFilter;
