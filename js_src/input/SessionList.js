import React from 'react';

const SessionList = ({ sessions, user, competition, setPage }) => {
    const sessionsRendered = sessions.map(session => {
        const goToPage = () => {
            setPage({
                'name': 'target',
                'api': session.api,
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
        <div className="session-selector">
            <div className="session-selector__event">{ competition.name } - Scoring</div>
            <div className="session-selector__archer">{ user }</div>
            { sessionsRendered }
        </div>
    );
};

export default SessionList;
