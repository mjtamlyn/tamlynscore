import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import EquipmentInspectionPage from './judging/EquipmentInspectionPage';

const app = document.getElementById('app');
const judgingApi = app.dataset.judgingApi;
const targetListApi = app.dataset.targetListApi;

const queryClient = new QueryClient();

if (app) {
    const root = createRoot(app);
    root.render(
        <StrictMode>
            <QueryClientProvider client={ queryClient }>
                <EquipmentInspectionPage judgingApi={ judgingApi } targetListApi={ targetListApi } />
            </QueryClientProvider>
        </StrictMode>
    );
}

