import React, { useContext, useState, useCallback } from 'react';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import axios from 'axios';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { AccountsContext } from '../AccountsContext';
import { PortfoliosContext } from '../PortfoliosContext';

function useDebounce(callback, delay) {
  const timeoutRef = React.useRef(null);

  const debounceFn = (...args) => {
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => {
      callback(...args);
    }, delay);
  };

  return debounceFn;
}

function TradeForm({ portfolio, onTradeAdded, onClose }) {
  const { accounts } = useContext(AccountsContext);
  const filteredBankAccounts = accounts.filter(account => account.entity === 'BRKR');
  const [tradeData, setTradeData] = useState({
    trade_id: "",
    timestamp: "",
    stock: "",
    quantity: "",
    price: "",
    operation: "BUY",
    portfolio: portfolio.url,
    tax: "",
    brokerage: ""
  });

  const [searchTerm, setSearchTerm] = useState('');
  const [stockSuggestions, setStockSuggestions] = useState([]);
  const [isDropdownVisible, setDropdownVisible] = useState(false);

  const fetchStocks = async (term) => {
    try {
      const response = await axios.get(`/portfolio/api/stocks/?symbol=${term}`);
      console.log(response.data);
      if (response.data.count > 0){
        setStockSuggestions(response.data.results); // Update the stockSuggestions state
        setDropdownVisible(true); 
      }
    } catch (error) {
      console.error("There was an error fetching stocks!", error);
    }
  };

  const debouncedFetchStocks = useDebounce(fetchStocks, 1000);

  const handleInputChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value); // Update searchTerm immediately to reflect in the input field
    if (value.trim()) {
      debouncedFetchStocks(value); // Debounced API call to fetch stocks
    }
    else {
      setDropdownVisible(false);  // Hide dropdown if input is empty
    }
  };

  const handleStockSelect = (stock) => {
    setTradeData({ ...tradeData, stock: stock.url });
    setSearchTerm(`${stock.market}:${stock.symbol}`);
    setDropdownVisible(false);  // Hide dropdown after selection
  };

  const handleChange = (e) => {
    setTradeData({ ...tradeData, [e.target.name]: e.target.value });
  };

  const handleTimestampChange = (date) => {
    setTradeData({ ...tradeData, timestamp: date });
  };

  const handleSubmit = (e, addAnother = false) => {
    e.preventDefault();

    axios.post('/portfolio/api/trades/', tradeData)
      .then(response => {
        onTradeAdded(response.data); // Notify parent component of the new trade

        if (addAnother) {
          // Clear the form but keep the modal open
          setTradeData({
            trade_id: "",
            timestamp: "",
            stock: "",
            quantity: "",
            price: "",
            operation: "BUY",
            portfolio: portfolio.url,
            tax: "",
            brokerage: ""
          });
        } else {
          // Close the modal
          onClose();
        }
      })
      .catch(error => {
        console.error("There was an error posting the trade!", error);
      });
  };

  return (
    <Form onSubmit={(e) => handleSubmit(e, false)}>
      <Form.Group className="mb-3" controlId="tf-tid">
        <Form.Label>Trade ID</Form.Label>
        <Form.Control
          type="text"
          placeholder="Trade ID"
          name="trade_id"
          value={tradeData.trade_id}
          onChange={handleChange}
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="tf-timestamp">
        <Form.Label>Timestamp</Form.Label>
        <DatePicker
          selected={tradeData.timestamp}
          onChange={handleTimestampChange}
          showTimeSelect
          dateFormat="Pp"
          className="form-control"
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="tf-stock">
        <Form.Label>Stock Symbol</Form.Label>
        <Form.Control
          type="text"
          name="stock"
          value={searchTerm}
          onChange={handleInputChange}
          required
          autoComplete="off"
        />
        {isDropdownVisible && stockSuggestions.length > 0 && (
          <ul className="stock-dropdown">
            {stockSuggestions.map(stock => (
              <li key={stock.id} onClick={() => handleStockSelect(stock)}>
                {stock.market}:{stock.symbol}
              </li>
            ))}
          </ul>
        )}
      </Form.Group>

      <Form.Group className="mb-3" controlId="tf-quantity">
        <Form.Label>Quantity</Form.Label>
        <Form.Control
          type="number"
          step="0.01"
          placeholder="0.00"
          name="quantity"
          value={tradeData.quantity}
          onChange={handleChange}
          required
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="tf-price">
        <Form.Label>Trade Price</Form.Label>
        <Form.Control
          type="number"
          step="0.01"
          placeholder="0.00"
          name="price"
          value={tradeData.price}
          onChange={handleChange}
          required
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="tf-tax">
        <Form.Label>Tax</Form.Label>
        <Form.Control
          type="number"
          step="0.01"
          placeholder="0.00"
          name="tax"
          value={tradeData.tax}
          onChange={handleChange}
          required
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="tf-brokerage">
        <Form.Label>Brokerage</Form.Label>
        <Form.Control
          type="number"
          step="0.01"
          placeholder="0.00"
          name="brokerage"
          value={tradeData.brokerage}
          onChange={handleChange}
          required
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="tf-operation">
        <Form.Label>Trade type</Form.Label>
        <Form.Select
          aria-label="Buy or Sell"
          name="operation"
          value={tradeData.operation}
          onChange={handleChange}
          required
        >
          <option value="BUY">Buy</option>
          <option value="SELL">Sell</option>
          <option value="SEED">Seed</option>
        </Form.Select>
      </Form.Group>

      <Button variant="primary" type="submit">
        Add Trade
      </Button>
      <Button variant="secondary" onClick={(e) => handleSubmit(e, true)} className="ms-2">
        Save and Add Another
      </Button>
    </Form>
  );
}

export default TradeForm;
