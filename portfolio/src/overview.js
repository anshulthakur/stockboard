import React from "react";
import { createRoot } from "react-dom/client";
import Dashboard from './components/Layout/Dashboard';
import DashboardCard from "./components/DashboardCard";
import Card from 'react-bootstrap/Card';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import PieChartCard from "./components/PieChartChard";


import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChartLine, faIndianRupeeSign, faPiggyBank } from '@fortawesome/free-solid-svg-icons';


const Overview = () => {
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
                      value="€0.00"
                      subtitle="Current invests: €7,547.50"
                      icon={<FontAwesomeIcon icon={faIndianRupeeSign} size="2x" />}
                  />
              </Col>
              <Col md={4} className="mb-3">
                  <DashboardCard
                      title="Gain"
                      value="€1,464.50"
                      subtitle="Total buy: €15,075.00. Total sell: €8,992.00"
                      icon={<FontAwesomeIcon icon={faChartLine} size="2x" />}
                  />
              </Col>
              <Col md={4} className="mb-3">
                  <DashboardCard
                      title="Fiat"
                      value="€1,500.00"
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