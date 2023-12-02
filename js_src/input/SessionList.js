import React, { useContext } from 'react';

import { CompetitionContext } from '../context/CompetitionContext';


const SessionList = ({ sessions, user, setPage }) => {
    const competition = useContext(CompetitionContext);

    const sessionsRendered = sessions.map(session => {
        const goToPage = () => {
            setPage({
                name: 'target',
                api: session.api,
            });
        };
        return (
            <div key={ session.start.iso } className="session-selector__session">
                <div className="session-selector__session__time">{ session.start.pretty }</div>
                <div className="session-selector__session__round">{ session.round } - Target { session.target }</div>
                <a onClick={ goToPage } className="session-selector__session__action">Enter scores</a>
            </div>
        );
    });
    return (
        <div className="full-height-page__card session-selector">
            <div className="session-selector__event">{ competition.name } - Scoring</div>
            <div className="session-selector__archer">{ user }</div>
            { sessionsRendered }
        </div>
    );
};

export default SessionList;
