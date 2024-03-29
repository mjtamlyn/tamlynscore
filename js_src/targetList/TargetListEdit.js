import React, { useContext, useState } from 'react';

import { CompetitionContext } from '../context/CompetitionContext';
import { TargetListContext } from '../context/TargetListContext';
import SessionList from './SessionList';

const TargetListEdit = () => {
    const competition = useContext(CompetitionContext);
    const targetList = useContext(TargetListContext);
    const [editMode, setEditMode] = useState(false);

    const sessionCount = targetList.sessions.size;
    let sessionColClass = {
        1: 'col3',
        2: 'col3',
        3: 'col2',
        4: 'col3',
    }[sessionCount];
    if (!sessionColClass) {
        sessionColClass = 'col2';
    }

    const sessions = Array.from(targetList.sessions.values().map(session => {
        return (
            <div className={ 'session ' + sessionColClass } key={ session.sessionTime }>
                <h4>{ session.sessionTime }</h4>
                <SessionList session={ session } editMode={ editMode } />
            </div>
        );
    }));
    return (
        <div className="target-list module">
            <h2>Target List</h2>
            <div className="row">
                <div className="col6">
                    <p>
                        <a className="btn" href={ `${competition.url}target-list/pdf/` }>View PDF (by round)</a>
                        &nbsp;
                        <a className="btn" href={ `${competition.url}target-list/pdf/?by_session=1` }>View PDF (by session)</a>
                        &nbsp;
                        { competition.isAdmin && <a className={ 'btn edit' + (editMode ? ' depressed' : '') } onClick={ () => setEditMode(!editMode) }>Edit</a> }
                    </p>
                </div>
            </div>
            <div className="row row--flex">
                { sessions }
            </div>
        </div>
    );
}

export default TargetListEdit;
