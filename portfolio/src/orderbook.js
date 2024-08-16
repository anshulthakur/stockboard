// orderbook.js
import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import '@fortawesome/fontawesome-svg-core/styles.css';

import { faChartLine, faChartPie, faMoneyBillWave, faWallet } from '@fortawesome/free-solid-svg-icons';


import DashboardCard from "./components/DashboardCard";
import WalletComponent from './components/WalletComponent'; // Adjust the path based on your folder structure
import Distribution from './components/Distribution';

import OrderBook from './components/OrderBook'; // Add the path

import { orderData } from './fixtures'; // Adjust path based on folder structure


const getTypeFromURL = () => {
  // Assuming the URL structure is /portfolio/:type/wallet
  const pathArray = window.location.pathname.split('/');
  return pathArray.includes('Crypto') ? 'crypto' : 'stock';
};

const Orders = () => {
  const type = getTypeFromURL();
//   const [data, setData] = useState(type === 'crypto' ? cryptoWalletData : stockWalletData);

//   useEffect(() => {
//     //console.log('Outer useEffect');
//     const fetchData = type === 'crypto' ? cryptoWalletData : stockWalletData;
//     setData(fetchData);
//   }, [type]);

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

  return (
    <div>
      <Container className="mt-4">
        {/* <h2>{type.charAt(0).toUpperCase() + type.slice(1)} Wallet</h2>*/ }
        <Row>
            <Col md={12}>
            <OrderBook />
            </Col>
        </Row>
      </Container>
    </div>
  );
}

const root = createRoot(document.getElementById("app"));
root.render(<Orders />);
