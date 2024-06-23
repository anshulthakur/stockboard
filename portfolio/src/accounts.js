import React from "react";
import { createRoot } from "react-dom/client";
import Dashboard from './components/Layout/Dashboard';
import Table from 'react-bootstrap/Table';

const Accounts = () => {
    return (
      <div>
        <Dashboard message="Welcome to the accounts listing page" />
      </div>
    );
  }

const root = createRoot(document.getElementById("app"));
root.render(<Accounts />);