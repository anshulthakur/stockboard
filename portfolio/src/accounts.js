import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import Dashboard from './components/Layout/Dashboard';
import Transactions from "./components/Layout/Transactions";
import TransactionForm from "./components/Layout/TransactionForm";
import AccountForm from "./components/AccountForm";
import Accordion from 'react-bootstrap/Accordion';
import Table from 'react-bootstrap/Table';
import Button from 'react-bootstrap/Button';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Nav from 'react-bootstrap/Nav';
import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';
import Modal from 'react-bootstrap/Modal';

import axios from "axios";
axios.defaults.headers.common['X-CSRFToken'] = csrftoken;

const Accounts = () => {
    const [accounts, setAccounts] = useState([]);
    const [showTransactionForm, setShowTransactionForm] = useState(false);
    const [showAccountForm, setShowAccountForm] = useState(false);
    const [currentAccountUrl, setCurrentAccountUrl] = useState(null);
    //const [transactions, setTransactions] = useState([]);
    const [transactionsByAccount, setTransactionsByAccount] = useState({});

    const transactionFormShow = (accountUrl) => {
      console.log('transactionFormShow');
      setCurrentAccountUrl(accountUrl);
      setShowTransactionForm(true);
    }
    const transactionFormHide = () => setShowTransactionForm(false);

    // Fetch account data from the API
    useEffect(() => {
      axios.get('/portfolio/api/accounts/')
          .then(response => {
              console.log(response);
              if (response.data.count != 0){
                setAccounts(response.data.results);
              }
          })
          .catch(error => {
              console.error("There was an error fetching the accounts!", error);
          });
    }, []);

    const fetchTransactions = (accountId) => {
      if (!transactionsByAccount[accountId]) {
        axios.get(`/portfolio/api/transactions/?account_id=${accountId}`)
          .then(response => {
            if (response.data.count !== 0) {
              console.log(response.data.results);
              setTransactionsByAccount(prevState => ({
                ...prevState,
                [accountId]: response.data.results
              }));
            }
          })
          .catch(error => {
            console.error("There was an error fetching the transactions!", error);
          });
      } //else {
        //setTransactions(transactionsByAccount[accountId]);
      //}
    };

    const accountFormShow = () => setShowAccountForm(true);
    const accountFormHide = () => setShowAccountForm(false);

    const handleAccountSubmit = async (newAccountData) => {
      // Handle the account creation logic, e.g., making an API call
      //setAccounts([...accounts, newAccountData]); // Update the state with the new account
      try {
        // Post the new account data to the backend API
        const response = await axios.post('/portfolio/api/accounts/', 
                                          newAccountData);
    
        // Assuming the response contains the newly created account
        const createdAccount = response.data;
    
        // Update the state with the new account
        setAccounts([...accounts, createdAccount]);
    
        // Optionally, handle any other success logic here
      } catch (error) {
        // Handle errors, e.g., display an error message to the user
        console.error("There was an error creating the account!", error);
      }
    };

    const handleTransactionAdded = () => {
      // Refresh the transaction list after adding a new transaction
      console.log('handleTransactionAdded');
      fetchTransactions(currentAccountUrl.split('/').slice(-2, -1)[0]);
    };

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
                          <Tabs defaultActiveKey={`summary-${index}`} id={`account-${index}`} className="mb-3">
                              <Tab eventKey={`summary-${index}`} title="Summary">
                                  <Table responsive striped bordered hover>
                                      <thead>
                                          <tr>
                                              <th>Account Name</th>
                                              <th>Account Number</th>
                                              <th>Type</th>
                                              <th>Currency</th>
                                              <th>Total Value</th>
                                              <th>Balance</th>
                                          </tr>
                                      </thead>
                                      <tbody>
                                          <tr>
                                              <td>{account.name}</td>
                                              <td>{account.account_id}</td>
                                              <td>{account.entity}</td>
                                              <td>{account.currency}</td>
                                              <td>{account.net_account_value}</td>
                                              <td>{account.cash_balance}</td>
                                          </tr>
                                      </tbody>
                                  </Table>
                              </Tab>
                              <Tab eventKey={`transactions-${index}`} 
                                    title="Transactions" 
                                    onEnter={() => fetchTransactions(account.id)}>
                                <Transactions 
                                  account_id={account.id} 
                                  transactions={transactionsByAccount[account.id] || []} 
                                  fetchTransactions={fetchTransactions} 
                                />
                                <Row className="justify-content-end mt-2">
                                    <Col xs={12} md={3}>
                                        <Button variant="primary" align="end" onClick={() => transactionFormShow(account.url)}>
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
                  <Button variant="primary" align="end" onClick={accountFormShow}>Add account</Button>{' '}
              </Nav.Item>
          </Nav>
          <Modal show={showTransactionForm} onHide={transactionFormHide}>
            <Modal.Header closeButton>
              <Modal.Title>Add transaction</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <TransactionForm 
                account_url={currentAccountUrl} 
                onTransactionAdded={handleTransactionAdded} 
                onClose={transactionFormHide} 
              />
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={transactionFormHide}>Close</Button>
            </Modal.Footer>
          </Modal>
          <Modal show={showAccountForm} onHide={accountFormHide}>
              <Modal.Header closeButton>
                  <Modal.Title>Add account</Modal.Title>
              </Modal.Header>
              <Modal.Body>
                  <AccountForm onSubmit={handleAccountSubmit} onClose={accountFormHide} />
              </Modal.Body>
          </Modal>
      </div>
    );
  }

const root = createRoot(document.getElementById("app"));
root.render(<Accounts />);