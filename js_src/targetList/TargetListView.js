import React from 'react';

import { TargetListProvider } from '../context/TargetListContext';
import View from '../utils/View';

import TargetListEdit from './TargetListEdit';

const TargetListView = ({ api }) => {
    return (
        <View api={ api } render={ data => {
            return (
                <TargetListProvider api={ api } targetList={ data.targetList }>
                    <TargetListEdit />
                </TargetListProvider>
            );
        } } Loading={
            () => <div>Loading...</div>
        }/>
    );
}

export default TargetListView;
