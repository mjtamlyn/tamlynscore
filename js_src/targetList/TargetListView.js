import React from 'react';

import Store from '../models/Store';
import TargetListSession from '../models/TargetListSession';
import View from '../utils/View';
import TargetListEdit from './TargetListEdit';

const TargetListView = ({ api }) => {
    return (
        <View api={ api } render={ data => {
            const targetList = data.targetList.map(session => new TargetListSession({ ...session }));
            const store = new Store({ api: api, data: targetList, dataName: 'targetList', autoSaveEnabled: false });
            return <TargetListEdit targetList={ targetList } store={ store } />;
        } } Loading={
            () => <div>Loading...</div>
        }/>
    );
}

export default TargetListView;
