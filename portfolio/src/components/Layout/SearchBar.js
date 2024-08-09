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

// const SearchBar = ({ placeholder, onSearch }) => {
//   const [searchTerm, setSearchTerm] = useState('');

//   const handleInputChange = (e) => {
//     setSearchTerm(e.target.value);
//   };

//   const handleSearch = () => {
//     onSearch(searchTerm);
//   };

//   return (
//     <div className="input-group mb-3">
//       <input
//         type="text"
//         className="form-control"
//         placeholder={placeholder}
//         value={searchTerm}
//         onChange={handleInputChange}
//       />
//       <div className="input-group-append">
//         <button className="btn btn-outline-secondary" type="button" onClick={handleSearch}>
//           Search
//         </button>
//       </div>
//     </div>
//   );
// };

// SearchBar.propTypes = {
//   placeholder: PropTypes.string,
//   onSearch: PropTypes.func.isRequired,
// };

export default SearchBar;
