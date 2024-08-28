import React, { useContext, useState } from 'react';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import axios from 'axios';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { AccountsContext

 } from '../AccountsContext';
function TransactionForm({ account, onTransactionAdded, onClose }) {
  const { accounts } = useContext(AccountsContext);
  const filteredBankAccounts = accounts.filter(account => account.entity !== 'DMAT');
  const [transactionData, setTransactionData] = useState({
    amount: "",
    transaction_type: "DB",
    notes: "",
    transaction_id: "",
    timestamp: new Date(), // Default to the current date and time
    source_account: account.url,
    destination_account: "", // Will be used only if transaction type is 'CR' or 'TR'
  });

  const handleChange = (e) => {
    setTransactionData({ ...transactionData, [e.target.name]: e.target.value });
  };

  const handleTimestampChange = (date) => {
    setTransactionData({ ...transactionData, timestamp: date });
  };

  const handleSubmit = (e, addAnother = false) => {
    e.preventDefault();
    
    // Adjust source and destination accounts based on transaction type
    if (transactionData.transaction_type === "CR") {
      transactionData.source_account = null;
      transactionData.destination_account = account.url;
    } else if (transactionData.transaction_type === "DB") {
      transactionData.source_account = account.url;
      transactionData.destination_account = null;
    }

    axios.post('/portfolio/api/transactions/', transactionData)
      .then(response => {
        onTransactionAdded(response.data); // Notify parent component of the new transaction
        
        if (addAnother) {
          // Clear the form but keep the modal open
          setTransactionData({
            amount: "",
            transaction_type: "DB",
            notes: "",
            transaction_id: "",
            timestamp: new Date(),
            source_account: account.url,
            destination_account: "",
          });
        } else {
          // Close the modal
          onClose();
        }
      })
      .catch(error => {
        console.error("There was an error posting the transaction!", error);
      });
  };

  return (
    <Form onSubmit={(e) => handleSubmit(e, false)}>
      <Form.Group className="mb-3" controlId="tf-tid">
        <Form.Label>Transaction ID</Form.Label>
        <Form.Control
          type="text"
          placeholder="Transaction ID"
          name="transaction_id"
          value={transactionData.transaction_id}
          onChange={handleChange}
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="tf-amount">
        <Form.Label>Amount</Form.Label>
        <Form.Control
          type="number"
          step="0.01"
          placeholder="0.00"
          name="amount"
          value={transactionData.amount}
          onChange={handleChange}
          required
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="tf-type">
        <Form.Label>Type</Form.Label>
        <Form.Select
          aria-label="Credit or Debit"
          name="transaction_type"
          value={transactionData.transaction_type}
          onChange={handleChange}
          required
        >
          <option value="DB">Debit</option>
          <option value="CR">Credit</option>
          <option value="TR">Transfer</option>
        </Form.Select>
      </Form.Group>

      <Form.Group className="mb-3" controlId="tf-info">
        <Form.Label>Transaction Information</Form.Label>
        <Form.Control
          type="text"
          placeholder="Transaction information"
          name="notes"
          value={transactionData.notes}
          onChange={handleChange}
        />
      </Form.Group>

      {transactionData.transaction_type === "TR" && (
        <Form.Group className="mb-3" controlId="tf-dest-account">
          <Form.Label>Destination Account</Form.Label>
          <Form.Control
            as="select"
            name="destination_account"
            value={transactionData.destination_account}
            onChange={handleChange}
            required
          >
            <option value="">Select Destination Account</option>
            {filteredBankAccounts.map(account => (
              <option key={account.id} value={account.url}>
                  {account.name}
              </option>
            ))}
          </Form.Control>
        </Form.Group>
      )}

      <Form.Group className="mb-3" controlId="tf-timestamp">
        <Form.Label>Timestamp</Form.Label>
        <DatePicker
          selected={transactionData.timestamp}
          onChange={handleTimestampChange}
          showTimeSelect
          dateFormat="Pp"
          className="form-control"
        />
      </Form.Group>

      <Button variant="primary" type="submit">
        Add Transaction
      </Button>
      <Button variant="secondary" onClick={(e) => handleSubmit(e, true)} className="ms-2">
        Save and Add Another
      </Button>
    </Form>
  );
}

export default TransactionForm;
