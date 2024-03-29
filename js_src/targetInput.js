import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import InputController from './input/InputController';

const app = document.getElementById('app');

if (app) {
    const root = createRoot(app);
    root.render(<StrictMode><InputController /></StrictMode>);
}
