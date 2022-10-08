import React from 'react';
import { createRoot } from 'react-dom/client';

import TargetInput from './input/TargetInput';

let app = document.getElementById('app');

if (app) {
    const root = createRoot(app);
    root.render(<TargetInput />);
}
