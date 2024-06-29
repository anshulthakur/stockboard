import React from "react";
import { createRoot } from "react-dom/client";
import Dashboard from './components/Layout/Dashboard';
import Card from 'react-bootstrap/Card';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Stack from 'react-bootstrap/Stack';

const Overview = () => {
    return (
      <div>
        <Dashboard message="Welcome to the overview page"/>
        <Container fluid>
          <Row xs={1} md={3} lg={4} className="g-4">
            <Col key="1">
              <Card>
                <Card.Header>
                  Portfolio value
                </Card.Header>
                <Card.Body>
                  <Card.Text>
                    Rs 10000
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col key="2">
              <Card>
                <Card.Header>
                  Booked Gains
                </Card.Header>
                <Card.Body>
                  <Card.Text>
                    +1000
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col key="3">
              <Card>
                <Card.Header>
                  Notional Gains
                </Card.Header>
                <Card.Body>
                  <Card.Text>
                    +5000 (100%)
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col key="4">
              <Card>
                <Card.Header>
                  Liquidity
                </Card.Header>
                <Card.Body>
                  <Card.Text>
                    1000
                  </Card.Text>
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