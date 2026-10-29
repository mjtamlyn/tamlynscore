import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import EquipmentInspectionPage from './judging/EquipmentInspectionPage';

const app = document.getElementById('app');
const judgingApi = app.dataset.judgingApi;

if (app) {
    const root = createRoot(app);
    root.render(<StrictMode><EquipmentInspectionPage judgingApi={ judgingApi } /></StrictMode>);
}

