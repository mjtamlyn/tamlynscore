import React from 'react';

import FullPageWrapper from './FullPageWrapper';
import Spinner from './Spinner';


const FullPageLoading = () => {
    return (
        <FullPageWrapper>
            <div className="full-height-page__loading">
                <Spinner white />
            </div>
        </FullPageWrapper>
    );
};

export default FullPageLoading;
