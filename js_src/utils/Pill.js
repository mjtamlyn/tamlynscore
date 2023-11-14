import React from 'react';

const Pill = ({ type, value }) => {
    const classes = ['pill', `pill--${type}`, `pill--${value.toLowerCase()}`];
    return <span className={ classes.join(' ') }>{ value }</span>;
};

export default Pill;
