import React from 'react';

import View from '../utils/View';
import TargetListEdit from './TargetListEdit';

const TargetListView = ({ api }) => {
    return (
        <View api={ api } render={
            data => <TargetListEdit targetList={ data.targetList } />
        } Loading={
            () => <div>Loading...</div>
        }/>
    );
}

export default TargetListView;
