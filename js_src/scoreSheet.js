import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import ScoreSheetPage from './input/ScoreSheetPage';

const app = document.getElementById('app');
const scoreApi = app.dataset.scoreApi;

if (app) {
    const root = createRoot(app);
    root.render(<StrictMode><ScoreSheetPage scoreApi={ scoreApi } /></StrictMode>);
}

