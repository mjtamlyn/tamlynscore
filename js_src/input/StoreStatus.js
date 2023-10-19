import React, { useState, useEffect } from 'react';

const StoreStatus = ({ store }) => {
    const [dirty, setDirty] = useState(store.dirty);
    const [loading, setLoading] = useState(store.loading);

    useEffect(() => {
        store.registerDirty(setDirty);
        store.registerLoading(setLoading);
        return () => {
            store.unregisterDirty(setDirty);
            store.unregisterLoading(setLoading);
        };
    }, [store]);

    return (
        <div className="sync-status">
            { dirty && "Data to save... " }
            { loading && "Saving..." }
        </div>
    );
};

export default StoreStatus;
