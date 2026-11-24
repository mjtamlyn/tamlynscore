import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import RegistrationPage from './registration/RegistrationPage';

const app = document.getElementById('app');
const targetListApi = app.dataset.targetListApi;

const queryClient = new QueryClient();

if (app) {
    const root = createRoot(app);
    root.render(
        <StrictMode>
            <QueryClientProvider client={ queryClient }>
                <RegistrationPage targetListApi={ targetListApi } />
            </QueryClientProvider>
        </StrictMode>
    );
}


