import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import DashboardCard from './DashboardCard';
import SearchBar from './Layout/SearchBar';
import { stockWalletData, cryptoWalletData } from '../fixtures';

const WalletComponent = ({ type }) => {
  const [data, setData] = useState(type === 'crypto' ? cryptoWalletData : stockWalletData);
  const [searchResults, setSearchResults] = useState(data.entries);

  useEffect(() => {
    const fetchData = type === 'crypto' ? cryptoWalletData : stockWalletData;
    setData(fetchData);
    setSearchResults(fetchData.entries);
  }, [type]);

//   useEffect(() => {
//     // Fetch wallet data based on type (crypto or stock)
//     const fetchData = async () => {
//       try {
//         const response = await axios.get(`/api/portfolio/${type}/wallet`);
//         setWalletData(response.data.entries);
//         setSummaryData(response.data.summary);
//       } catch (error) {
//         console.error('Error fetching wallet data:', error);
//       }
//     };

//     fetchData();
//   }, [type]);

  const handleSearch = (searchTerm) => {
    const results = data.entries.filter(item =>
      item.symbol.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setSearchResults(results);
  };

  return (
    <div>
      <h2>{type.charAt(0).toUpperCase() + type.slice(1)} Wallet</h2>
      <div className="row">
        <DashboardCard title="Cost" value={data.summary.cost} subtitle={`Current invest: ${data.summary.previousDay}`} icon="fa-wallet" />
        <DashboardCard title="Wallet Value" value={data.summary.walletValue} subtitle={`Previous day: ${data.summary.previousDay}`} icon="fa-money-bill-wave" />
        <DashboardCard title="Current W/L" value={data.summary.currentWL} subtitle="-80.21%" icon="fa-chart-line" />
        <DashboardCard title="Materialized W/L" value={data.summary.materializedWL} subtitle="" icon="fa-chart-pie" />
      </div>
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

// const root = createRoot(document.getElementById("app"));
// root.render(<WalletComponent type={window.location.pathname.split('/')[2]} />);

export default WalletComponent;