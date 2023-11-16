import React from 'react';

const Spinner = ({ white = false }) => {
    return (
        <ul className={ 'loading__spinner' + (white ? ' loading__spinner--white' : '') }>
          <li className="loading__spinner--center"></li>
          <li className="loading__spinner__item loading__spinner__item--1"></li>
          <li className="loading__spinner__item loading__spinner__item--2"></li>
          <li className="loading__spinner__item loading__spinner__item--3"></li>
          <li className="loading__spinner__item loading__spinner__item--4"></li>
          <li className="loading__spinner__item loading__spinner__item--5"></li>
          <li className="loading__spinner__item loading__spinner__item--6"></li>
          <li className="loading__spinner__item loading__spinner__item--7"></li>
          <li className="loading__spinner__item loading__spinner__item--8"></li>
        </ul>
    );
};

export default Spinner;
