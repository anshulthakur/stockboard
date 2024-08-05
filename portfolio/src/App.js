import React from 'react'
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Dashboard from './components/Layout/Dashboard';
import WalletComponent from './components/WalletComponent';

const App = () => {
  return (
    <Router>
      <Switch>
        <Route exact path="/" component={Dashboard} />
        <Route path="/portfolio/:type/wallet" component={WalletComponent} />
        {/* Add other routes as needed */}
      </Switch>
    </Router>
  );
}

export default App