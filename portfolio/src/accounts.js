import React from "react";
import { useState } from 'react';
import { createRoot } from "react-dom/client";
import Dashboard from './components/Layout/Dashboard';
import Transactions from "./components/Layout/Transactions";
import TransactionForm from "./components/Layout/TransactionForm";
import Accordion from 'react-bootstrap/Accordion';
import Table from 'react-bootstrap/Table';
import Button from 'react-bootstrap/Button';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Nav from 'react-bootstrap/Nav';
import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';
import Modal from 'react-bootstrap/Modal';

var account_fixtures = [
  {
    account_id: 1,
    name: 'Canara',
    entity: 'BANK',
    currency: 'INR',
    amount: 1234
  },
  {
    account_id: 2,
    name: 'Zerodha',
    entity: 'BROKER',
    currency: 'INR',
    amount: 2345
  },
  {
    account_id: 3,
    name: 'WazirX',
    entity: 'EXCHANGE',
    currency: 'INR',
    amount: 1234
  },
];

const Accounts = () => {
    let accounts = account_fixtures;
    const [showTransactionForm, setShowTransactionForm] = useState(false);

    const transactionFormShow = () => setShowTransactionForm(true);
    const transactionFormHide = () => setShowTransactionForm(false);
    return (
      <div>
        <Dashboard message="Welcome to the accounts listing page" />
        <Accordion>
          {accounts.map((account, index) => (
            <Accordion.Item eventKey={index} key={index}>
              <Accordion.Header>
                {account.name}
              </Accordion.Header>
              <Accordion.Body>
                <Tabs
                  defaultActiveKey="summary-{index}"
                  id="account-{index}"
                  className="mb-3"
                >
                  <Tab eventKey="summary-{index}" title="Summary">
                    <Table responsive striped bordered hover>
                      <thead>
                        <tr>
                          <th>Account Name</th>
                          <th>Account Number</th>
                          <th>Type</th>
                          <th>Currency</th>
                          <th>Amount</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                        <td>{account.name}</td>
                        <td>{account.account_id}</td>
                        <td>{account.entity}</td>
                        <td>{account.currency}</td>
                        <td>{account.amount}</td>
                        </tr>
                      </tbody>
                    </Table>
                  </Tab>
                  <Tab eventKey="transactions-{index}" title="Transactions">
                    <Transactions account_id="1" />
                    <Row className="justify-content-end mt-2" >
                      <Col xs={12} md={3}>
                        <Button variant="primary" align="end" onClick={transactionFormShow}>
                          Add transactions
                        </Button>{' '}
                      </Col>
                    </Row>
                  </Tab>
                </Tabs>
              </Accordion.Body>
            </Accordion.Item>
            ))}
        </Accordion>
        <Nav variant="pills">
          <Nav.Item>
            <Button variant="primary" align="end">Add account</Button>{' '}
          </Nav.Item>
        </Nav>
        <Modal show={showTransactionForm} onHide={transactionFormHide}>
          <Modal.Header closeButton>
            <Modal.Title>Add transaction</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <TransactionForm />
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={transactionFormHide}>
              Close
            </Button>
            <Button variant="primary" onClick={transactionFormHide}>
              Save
            </Button>
          </Modal.Footer>
        </Modal>
      </div>
    );
  }

const root = createRoot(document.getElementById("app"));
root.render(<Accounts />);