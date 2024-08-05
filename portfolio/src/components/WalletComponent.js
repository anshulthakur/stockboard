import React, { useState, useEffect } from 'react';
import SearchBar from './Layout/SearchBar';

const WalletComponent = ({ type, data }) => {
  const [searchResults, setSearchResults] = useState(data.entries);

  const handleSearch = (searchTerm) => {
    const results = data.entries.filter(item =>
      item.symbol.toLowerCase().includes(searchTerm.toLowerCase())
    );
    console.log('handleSearch');
    console.log(results);
    setSearchResults(results);
  };

  // useState(() => {
  //   console.log('useState');
  //   console.log(data);
  //   setSearchResults(data);
  // }, [data]);

  console.log('render');
  console.log(data.entries);
  return (
    <div>
      <SearchBar placeholder="Search by symbol" onSearch={handleSearch} />
      <table className="table table-striped">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Shares</th>
            <th>Price</th>
            <th>Cost</th>
            <th>Current Price</th>
            <th>Value</th>
            <th>W/L</th>
            <th>Day Change</th>
            <th>Pre Change</th>
          </tr>
        </thead>
        <tbody>
          {searchResults.map(item => (
            <tr key={item.symbol}>
              <td>{item.symbol}</td>
              <td>{item.shares}</td>
              <td>{item.price}</td>
              <td>{item.cost}</td>
              <td>{item.currentPrice}</td>
              <td>{item.value}</td>
              <td>{item.wl}</td>
              <td>{item.dayChange}</td>
              <td>{item.preChange}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default WalletComponent;