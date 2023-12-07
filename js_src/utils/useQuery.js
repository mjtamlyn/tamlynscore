import { useState, useEffect } from 'react';


const useQuery = (api) => {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);

    useEffect(() => {
        if (loading) {
            fetch(api).then(response => response.json()).then(data => {
                setLoading(false);
                setData(data);
            });
        }
    }, [api, loading]);

    return [data, loading];
};

export default useQuery;
