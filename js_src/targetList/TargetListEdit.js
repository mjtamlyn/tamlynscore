import React from 'react';

const Session = ({ sessionTime }) => {
    return (
        <h4>{ sessionTime }</h4>
    );
}

const TargetListEdit = ({ targetList }) => {
    const sessionCount = targetList.length;
    let sessionColClass = {
        1: 'col3',
        2: 'col3',
        3: 'col2',
        4: 'col3',
    }[sessionCount];
    if (!sessionColClass) {
        sessionColClass = 'col2';
    }

    const sessions = targetList.map(session => {
        return (
            <div className={ 'session ' + sessionColClass } key={ session.sessionTime }>
                <Session sessionTime={ session.sessionTime } />
            </div>
        );
    });
    return (
        <div className="container">
            <div className="target-list module">
                <h2>Target List</h2>
                <div className="row">
                    <div className="col6">
                        Buttons here
                    </div>
                </div>
                <div className="row row--flex">
                    { sessions }
                </div>
            </div>
        </div>
    );
}

export default TargetListEdit;
