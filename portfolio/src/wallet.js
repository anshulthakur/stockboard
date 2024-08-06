// wallet.js
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
import { stockWalletData, cryptoWalletData } from './fixtures';

const getTypeFromURL = () => {
  // Assuming the URL structure is /portfolio/:type/wallet
  const pathArray = window.location.pathname.split('/');
  return pathArray.includes('Crypto') ? 'crypto' : 'stock';
};

const Wallet = () => {
  const type = getTypeFromURL();
  const [data, setData] = useState(type === 'crypto' ? cryptoWalletData : stockWalletData);

  useEffect(() => {
    //console.log('Outer useEffect');
    const fetchData = type === 'crypto' ? cryptoWalletData : stockWalletData;
    setData(fetchData);
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

  return (
    <div>
      <Container className="mt-4">
        {/* <h2>{type.charAt(0).toUpperCase() + type.slice(1)} Wallet</h2>*/ }
        <Tabs defaultActiveKey="wallet" id="wallet-tabs" className="mb-3">
          <Tab eventKey="wallet" title="Wallet">
            <Row>
              <Col md={4} className="mb-3">
              <DashboardCard title="Cost" 
                            value={data.summary.cost} 
                            subtitle={`Current invest: ${data.summary.previousDay}`} 
                            icon={<FontAwesomeIcon icon={faWallet} size="2x" />}
                            />
              </Col>
              <Col md={4} className="mb-3">
              <DashboardCard title="Wallet Value" 
                            value={data.summary.walletValue} 
                            subtitle={`Previous day: ${data.summary.previousDay}`} 
                            icon={<FontAwesomeIcon icon={faMoneyBillWave} size="2x" />}
                            />
              </Col>
              <Col md={4} className="mb-3">
              <DashboardCard title="Current W/L" 
                            value={data.summary.currentWL} 
                            subtitle="-80.21%" 
                            icon={<FontAwesomeIcon icon={faChartLine} size="2x" />} 
                            />
              </Col>
              <Col md={4} className="mb-3">
              <DashboardCard title="Materialized W/L" 
                              value={data.summary.materializedWL} 
                              subtitle="" 
                              icon={<FontAwesomeIcon icon={faChartPie} size="2x" />} 
                              />
              </Col>
            </Row>
            <Row>
              <WalletComponent type={type} data={data} />
            </Row>
          </Tab>
          <Tab eventKey="distribution" title="Distribution">
            <Distribution type={type} data={data} />
          </Tab>
        </Tabs>
      </Container>
    </div>
  );
}

const root = createRoot(document.getElementById("app"));
root.render(<Wallet />);
