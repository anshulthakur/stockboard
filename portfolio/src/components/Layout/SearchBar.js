// SearchBar.js
import React, { useState } from 'react';
import PropTypes from 'prop-types';

const SearchBar = ({ placeholder, searchQuery, setSearchQuery }) => {
  return (
      <input
          type="text"
          placeholder={placeholder}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="form-control"
      />
  );
};

export default SearchBar;
