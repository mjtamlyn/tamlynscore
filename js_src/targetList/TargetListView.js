import React from 'react';

import View from '../utils/View';
import TargetListEdit from './TargetListEdit';

const TargetListView = () => {
    return (
        <View api="/tournaments/wallingford-is-2-2023/target-list/api/" render={
            data => <TargetListEdit targetList={ data.targetList } />
        } Loading={
            () => <div>Loading...</div>
        }/>
    );
}

export default TargetListView;
