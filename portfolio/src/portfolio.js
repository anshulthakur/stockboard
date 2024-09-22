import React, { useContext, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import Dashboard from './components/Layout/Dashboard';
import Trades from "./components/Layout/Trades";
import TradeForm from "./components/Layout/TradeForm";
import PortfolioForm from "./components/PortfolioForm";
import CsvUploader from './components/CsvUploader'; // CSV Uploader component
import Accordion from 'react-bootstrap/Accordion';
import Table from 'react-bootstrap/Table';
import Button from 'react-bootstrap/Button';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Nav from 'react-bootstrap/Nav';
import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';
import Modal from 'react-bootstrap/Modal';
import SearchBar from './components/Layout/SearchBar'; // Search Bar component
import PaginationComponent from './components/Layout/Pagination'; // Pagination component
import useDebounce from "./utils/debounce";

import { AccountsContext, AccountsProvider } from "./components/AccountsContext";
import { PortfoliosContext, PortfoliosProvider } from "./components/PortfoliosContext";
import axios from "axios";
axios.defaults.headers.common['X-CSRFToken'] = csrftoken;

const getAccountByUrl = (url, accounts) => {
  for (const account of accounts) {
    if (url === account.url) {
      return account;
    }
  }
  return null;
};

const Portfolio = () => {
    const { accounts } = useContext(AccountsContext); // Access accounts data
    const { portfolios, setPortfolios} = useContext(PortfoliosContext);

    const [showTradeForm, setShowTradeForm] = useState(false);
    const [showPortfolioForm, setShowPortfolioForm] = useState(false);
    const [currentPortfolio, setCurrentPortfolio] = useState(null);
    const [tradesByPortfolio, setTradesByPortfolio] = useState({});
    const [searchQuery, setSearchQuery] = useState(''); // Search query state
    const [currentPage, setCurrentPage] = useState(1); // Pagination state
    const [showCsvModal, setShowCsvModal] = useState(false); // State for CSV modal

    const debouncedSearchQuery = useDebounce(fetchTrades, 1000); //Filter after the user intention

    const tradeFormShow = (portfolio) => {
      console.log('tradeFormShow', portfolio);
      setCurrentPortfolio(portfolio);
      setShowTradeForm(true);
    }
    const tradeFormHide = () => setShowTradeForm(false);

    const itemsPerPage = 10;

    const fetchTrades = (portfolioId, query = '', page = 1) => {
      console.log('fetchTrades');
      const url = `/portfolio/api/trades/?portfolio_id=${portfolioId}&search=${query}&page=${page}`;
      axios.get(url)
        .then(response => {
          if (response.data.count !== 0) {
            console.log('Fetched trades for portfolio ID ', portfolioId);
            console.log(response.data.results);
            setTradesByPortfolio(prevState => ({
              ...prevState,
              [portfolioId]: {
                trades: response.data.results,
                totalItems: response.data.count
              }
            }));
          }
        })
        .catch(error => {
          console.error("There was an error fetching the trades!", error);
        });
    };

    const handleCsvSubmit = (data) => {
      console.log('CSV data submitted:', data);
      // Bulk trades have been added, refresh trade data
      fetchTrades(currentPortfolio.url.split('/').slice(-2, -1)[0]);
    };

    const portfolioFormShow = () => setShowPortfolioForm(true);
    const portfolioFormHide = () => setShowPortfolioForm(false);

    const handlePortfolioSubmit = async (newPortfolioData) => {
      // Handle the portfolio creation logic, e.g., making an API call
      try {
        // Post the new account data to the backend API
        const response = await axios.post('/portfolio/api/portfolios/', 
          newPortfolioData);
    
        // Assuming the response contains the newly created account
        const createdPortfolio = response.data;
    
        // Update the state with the new portfolio
        setPortfolios([...portfolios, createdPortfolio]);
        // Optionally, handle any other success logic here
      } catch (error) {
        // Handle errors, e.g., display an error message to the user
        console.error("There was an error creating the portfolio!", error);
      }
    };

    const handleTradeAdded = () => {
      // Refresh the trade list after adding a new trade
      console.log('handleTradeAdded');
      fetchTrades(currentPortfolio.url.split('/').slice(-2, -1)[0]);
    };

    return (
      <div>
          <Dashboard message="Welcome to the portfolio listing page" />
          <Accordion>
              {
                portfolios.map((portfolio, index) => {
                let account = getAccountByUrl(portfolio.account, accounts);
                console.log(account);
                return(
                  <Accordion.Item eventKey={index} key={index}>
                      <Accordion.Header>
                          {portfolio.name}
                      </Accordion.Header>
                      <Accordion.Body>
                          <Tabs defaultActiveKey={`summary-${index}`} id={`portfolio-${index}`} className="mb-3">
                              <Tab eventKey={`summary-${index}`} title="Summary">
                                  <Table responsive striped bordered hover>
                                      <thead>
                                          <tr>
                                              <th>Portfolio Name</th>
                                              <th>Broker Name</th>
                                              <th>Total Invested Value</th>
                                              <th>Total Current Value</th>
                                              <th>Realized gains</th>
                                          </tr>
                                      </thead>
                                      <tbody>
                                          <tr>
                                              <td>{portfolio.name}</td>
                                              <td>{account.name}</td>
                                              <td>{portfolio.invested_value}</td>
                                              <td>{portfolio.current_value}</td>
                                              <td>{parseFloat(portfolio.realized_profit.sell_trades)-parseFloat(portfolio.realized_profit.buy_trades)}</td>
                                          </tr>
                                      </tbody>
                                  </Table>
                              </Tab>
                              <Tab eventKey={`trades-${index}`} 
                                    title="Trades" 
                                    onEnter={() => {
                                      console.log('onEnter called');
                                      setCurrentPortfolio(portfolio);
                                      if (!tradesByPortfolio[portfolio.id]) {
                                        fetchTrades(portfolio.id, searchQuery, currentPage); // Only fetch if not already fetched
                                      }
                                    }}>
                                <SearchBar searchQuery={searchQuery} setSearchQuery={(q) => { 
                                    console.log('SearchBar setquery');
                                    setSearchQuery(q); 
                                    debouncedSearchQuery(portfolio.id, q, currentPage);
                                  }} />
                                <Trades 
                                  portfolio={portfolio} 
                                  trades={tradesByPortfolio[portfolio.id]?.trades || []} 
                                />
                                {/* Pagination Component */}
                                <PaginationComponent 
                                  itemsPerPage={itemsPerPage} 
                                  totalItems={tradesByPortfolio[portfolio.id]?.totalItems || 0}
                                  currentPage={currentPage}
                                  setCurrentPage={(page) => {
                                    console.log('setCurrentPage');
                                    setCurrentPage(page);
                                    fetchTrades(portfolio.id, searchQuery, page);
                                  }}
                                />
                                <Row className="justify-content-end mt-2">
                                    <Col xs={12} md={3}>
                                        <Button variant="primary" align="end" onClick={() => tradeFormShow(portfolio)}>
                                            Add trades
                                        </Button>{' '}
                                    </Col>
                                    <Col xs={12} md={3}>
                                      <Button variant="secondary" onClick={() => setShowCsvModal(true)}>
                                        Upload CSV
                                      </Button>
                                    </Col>
                                </Row>
                              </Tab>
                          </Tabs>
                      </Accordion.Body>
                  </Accordion.Item>
                )})
              }
          </Accordion>

          {/* Add Portfolio Modal */}
          <Nav variant="pills">
              <Nav.Item>
                  <Button variant="primary" align="end" onClick={portfolioFormShow}>Add portfolio</Button>{' '}
              </Nav.Item>
          </Nav>

          {/* Trade Form Modal */}
          <Modal show={showTradeForm} onHide={tradeFormHide}>
            <Modal.Header closeButton>
              <Modal.Title>Add trade</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <TradeForm 
                portfolio={currentPortfolio} 
                onTradeAdded={handleTradeAdded} 
                onClose={tradeFormHide} 
              />
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={tradeFormHide}>Close</Button>
            </Modal.Footer>
          </Modal>
          
          {/* CSV Upload Modal */}
          <Modal show={showCsvModal} onHide={() => setShowCsvModal(false)} size="xl">
            <Modal.Header closeButton>
              <Modal.Title>Upload CSV</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <CsvUploader onSubmit={handleCsvSubmit} handleClose={() => setShowCsvModal(false)} currentPortfolio={currentPortfolio} />
            </Modal.Body>
          </Modal>

          {/* Portfolio Form Modal */}
          <Modal show={showPortfolioForm} onHide={portfolioFormHide}>
              <Modal.Header closeButton>
                  <Modal.Title>Add portfolio</Modal.Title>
              </Modal.Header>
              <Modal.Body>
                  <PortfolioForm onSubmit={(newPortfolioData) => {
                      handlePortfolioSubmit(newPortfolioData);
                      setShowPortfolioForm(false);
                    }} 
                    onClose={portfolioFormHide} />
              </Modal.Body>
          </Modal>
      </div>
    );
  }

const root = createRoot(document.getElementById("app"));
root.render(<AccountsProvider>
  <PortfoliosProvider>
    <Portfolio />
  </PortfoliosProvider>
</AccountsProvider>);