import React, { useState, useEffect } from 'react';
import SearchBar from './Layout/SearchBar';
import PaginationComponent from './Layout/Pagination';

const WalletComponent = ({ type, data }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Filter results based on search query
  const filteredResults = data.entries.filter(item =>
    item.symbol.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Handle Search
  const handleSearch = (searchTerm) => {
    const results = data.entries.filter(item =>
      item.symbol.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setSearchResults(results);
    setCurrentPage(1); // Reset to the first page on a new search
  };

  // useState(() => {
  //   console.log('useState');
  //   console.log(data);
  //   setSearchResults(data);
  // }, [data]);

  // Pagination Logic
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = filteredResults.slice(indexOfFirstItem, indexOfLastItem);

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  //console.log('render');
  //console.log(data.entries);
  return (
    <div>
      <SearchBar placeholder="Search by symbol" searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
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
          {currentItems.map(item => (
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
      <PaginationComponent 
        itemsPerPage={itemsPerPage} 
        totalItems={filteredResults.length} 
        paginate={paginate} 
        currentPage={currentPage}
      />
    </div>
  );
};

export default WalletComponent;