import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import ResultsPage from './results/ResultsPage';

const app = document.getElementById('app');
const resultsApi = app.dataset.resultsApi;

if (app) {
    const root = createRoot(app);
    root.render(<StrictMode><ResultsPage resultsApi={ resultsApi } /></StrictMode>);
}
