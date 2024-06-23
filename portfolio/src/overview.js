import React from "react";
import { createRoot } from "react-dom/client";
import Dashboard from './components/Layout/Dashboard';

const Overview = () => {
    return (
      <div>
        <Dashboard message="Welcome to the overview page"/>
      </div>
    );
  }

const root = createRoot(document.getElementById("app"));
root.render(<Overview />);