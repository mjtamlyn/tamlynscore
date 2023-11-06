import React from 'react';
import { createRoot } from 'react-dom/client';

import TargetListView from './targetList/TargetListView';

let app = document.getElementById('app');

if (app) {
    const root = createRoot(app);
    root.render(<TargetListView />);
}
