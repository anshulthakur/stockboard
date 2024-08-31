import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

// Create the context
export const PortfoliosContext = createContext();

// Create a provider component
export const PortfoliosProvider = ({ children }) => {
    const [portfolios, setPortfolios] = useState([]);

    // Fetch account data from the API once when the component is mounted
    useEffect(() => {
        axios.get('/portfolio/api/portfolios/')
            .then(response => {
                console.log(response);
                if (response.data.count !== 0) {
                    setPortfolios(response.data.results);
                }
            })
            .catch(error => {
                console.error("There was an error fetching the portfolios!", error);
            });
    }, []);

    return (
        <PortfoliosContext.Provider value={{ portfolios, setPortfolios }}>
            {children}
        </PortfoliosContext.Provider>
    );
};