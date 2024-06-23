import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Layout/Dashboard';

const App = () => {
  return (
    <div>
      <Dashboard />
    </div>
  );
}

export default App