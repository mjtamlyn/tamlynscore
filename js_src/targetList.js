import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import TargetListView from './targetList/TargetListView';

let app = document.getElementById('app');

if (app) {
    const root = createRoot(app);
    root.render(<StrictMode><TargetListView api={ app.dataset.apiUrl } /></StrictMode>);
}
