import React from 'react';

import Pill from '../utils/Pill';

const ArcherBlock = ({ place, archer }) => {
    if (archer) {
        return (
            <div className="archer-block">
                <div className="name">
                    <p>
                        <span className="detail">{ place }</span>
                        <span className="name">{ archer.name }</span>
                    </p>
                </div>
                <div className="bottom">
                    <p>{ archer.club }</p>
                    <p>
                        <Pill type="bowstyle" value={ archer.bowstyle } />
                        &nbsp;
                        { archer.age && <Pill type="age" value={ archer.age } /> }
                        { archer.age && ' ' }
                        <Pill type="gender" value={ archer.gender } />
                    </p>
                </div>
            </div>
        );
    }
    return (
        <div className="archer-block">
            <div className="name">
                <p>
                    <span className="detail">{ place }</span>
                </p>
            </div>
            <div className="bottom"></div>
        </div>
    );
}

const Boss = ({ number, archers }) => {
    return (
        <div className="boss">
            <ArcherBlock place={ `${number}A` } archer={ archers.A } />
            <ArcherBlock place={ `${number}B` } archer={ archers.B } />
            <ArcherBlock place={ `${number}C` } archer={ archers.C } />
            <ArcherBlock place={ `${number}D` } archer={ archers.D } />
        </div>
    );
}

const SessionList = ({ targets }) => {
    const bosses = targets.map(boss => <Boss number={ boss.number} archers={ boss.archers } key={ boss.number } />);
    return bosses;
}

export default SessionList;
