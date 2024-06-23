// In a navigation component or menu

import React from 'react';
import { Link } from 'react-router-dom';

const Navigation = () => {
  return (
    <nav>
      <ul>
        <li>
          <Link to="/overview">Projects</Link>
        </li>
        <li>
          <Link to="/accounts">Accounts</Link> {/* Link to the Planning Page */}
        </li>
      </ul>
    </nav>
  );
};

export default Navigation;