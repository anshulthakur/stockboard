import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import Dashboard from './components/Layout/Dashboard';
import DashboardCard from "./components/DashboardCard";
import Card from 'react-bootstrap/Card';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import PieChartCard from "./components/PieChartChard";

import axios from "axios";

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChartLine, faIndianRupeeSign, faPiggyBank } from '@fortawesome/free-solid-svg-icons';


const Overview = () => {
    const [financialData, setFinancialData] = useState({
        net_worth: "0.00",
        net_gains: "0.00",
        net_invested_value: "0.00",
        total_buy_value: "0.00",
        total_sell_value: "0.00",
        fiat_liquidity: "0.00",
    });

    useEffect(() => {
        axios.get('/portfolio/api/user/summary/')
            .then(response => {
                const data = response.data;

                // Handle null values by defaulting to "₹0.00"
                setFinancialData({
                    net_worth: data.net_worth !== null ? `${data.net_worth}` : "0.00",
                    net_gains: data.net_gains !== null ? `${data.net_gains}` : "0.00",
                    net_invested_value: data.net_invested_value !== null ? `${data.net_invested_value}` : "0.00",
                    total_buy_value: data.total_buy_value !== null ? `${data.total_buy_value}` : "0.00",
                    total_sell_value: data.total_sell_value !== null ? `${data.total_sell_value}` : "0.00",
                    fiat_liquidity: data.fiat_liquidity !== null ? `${data.fiat_liquidity}` : "0.00",
                });
            })
            .catch(error => {
                console.error("There was an error fetching the financial data!", error);
            });
    }, []);

    const portfolioData = {
        labels: ['Degiro acc', 'Bitstamp acc'],
        values: [60, 40],
    };

    const investPercentageData = {
        labels: ['Degiro acc'],
        values: [100],
    };

    return (
      <div>
        <Dashboard message="Welcome to the overview page"/>
        <Container className="mt-4">
          <Row>
          <Col md={4} className="mb-3">
                  <DashboardCard
                      title="Portfolio Value"
                      value={`₹${financialData.net_worth}`}
                      subtitle={`Current invests: ₹${financialData.net_invested_value}`}
                      icon={<FontAwesomeIcon icon={faIndianRupeeSign} size="2x" />}
                  />
              </Col>
              <Col md={4} className="mb-3">
                  <DashboardCard
                      title="Gain"
                      value={`₹${financialData.net_gains}`}
                      subtitle={`Total buy: ₹${financialData.total_buy_value}. Total sell: ₹${financialData.total_sell_value}`}
                      icon={<FontAwesomeIcon icon={faChartLine} size="2x" />}
                  />
              </Col>
              <Col md={4} className="mb-3">
                  <DashboardCard
                      title="Fiat"
                      value={`₹${financialData.fiat_liquidity}`}
                      icon={<FontAwesomeIcon icon={faPiggyBank} size="2x" />}
                  />
              </Col>
          </Row>
          <Row>
              <Col md={4} className="mb-3">
                  <PieChartCard title="Total Portfolio" data={portfolioData} />
              </Col>
              <Col md={4} className="mb-3">
                  <PieChartCard title="Invest Percentage" data={investPercentageData} />
              </Col>
              <Col md={4} className="mb-3">
                  <Card className="text-center">
                      <Card.Body>
                          <Card.Title>Bank percentage - Not implemented</Card.Title>
                      </Card.Body>
                  </Card>
              </Col>
          </Row>
        </Container>
      </div>
    );
  }

const root = createRoot(document.getElementById("app"));
root.render(<Overview />);