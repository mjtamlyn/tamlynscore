import React from 'react';
import { createRoot } from 'react-dom/client';

import Target from './input/Target';

let app = document.getElementById('app');

if (app) {
    const root = createRoot(app);
    root.render(<Target />);
}
