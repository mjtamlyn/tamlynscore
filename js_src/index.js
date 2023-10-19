import React from 'react';
import { createRoot } from 'react-dom/client';

import InputController from './input/InputController';

let app = document.getElementById('app');

if (app) {
    const root = createRoot(app);
    root.render(<InputController />);
}
