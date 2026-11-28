import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const app = document.getElementById('app');
const inputApi = app.dataset.inputApi;

const queryClient = new QueryClient();

if (app) {
    const root = createRoot(app);
    root.render(
        <StrictMode>
            <QueryClientProvider client={ queryClient }>
                { inputApi }
            </QueryClientProvider>
        </StrictMode>
    );
}



