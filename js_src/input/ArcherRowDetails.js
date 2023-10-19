import React from 'react';


const ArcherRowDetails = ({ score }) => {
    return (
        <>
            <div className="archers__target">{ score.target }</div>
            <div className="archers__name">{ score.name }</div>
            <div className="archers__categories">
                <span className={ 'pill bowstyle ' + score.categories.bowstyle.toLowerCase() }>{ score.categories.bowstyle }</span>
                &nbsp;
                <span className={ 'pill gender ' + score.categories.gender.toLowerCase() }>{ score.categories.gender }</span>
            </div>
        </>
    )
};

export default ArcherRowDetails;
