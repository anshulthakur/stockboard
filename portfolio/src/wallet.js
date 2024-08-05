// wallet.js
import React from 'react';
import { createRoot } from 'react-dom/client';
import WalletComponent from './components/WalletComponent'; // Adjust the path based on your folder structure

const getTypeFromURL = () => {
  // Assuming the URL structure is /portfolio/:type/wallet
  const pathArray = window.location.pathname.split('/');
  return pathArray.includes('crypto') ? 'crypto' : 'stock';
};

const type = getTypeFromURL();

const root = createRoot(document.getElementById("app"));
root.render(<WalletComponent type={type} />);
