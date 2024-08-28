import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

// Create the context
export const AccountsContext = createContext();

// Create a provider component
export const AccountsProvider = ({ children }) => {
    const [accounts, setAccounts] = useState([]);

    // Fetch account data from the API once when the component is mounted
    useEffect(() => {
        axios.get('/portfolio/api/accounts/')
            .then(response => {
                console.log(response);
                if (response.data.count !== 0) {
                    setAccounts(response.data.results);
                }
            })
            .catch(error => {
                console.error("There was an error fetching the accounts!", error);
            });
    }, []);

    return (
        <AccountsContext.Provider value={{ accounts, setAccounts }}>
            {children}
        </AccountsContext.Provider>
    );
};