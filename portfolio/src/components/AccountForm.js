import React, { useState } from "react";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";

const AccountForm = ({ onSubmit, onClose }) => {
  const [accountData, setAccountData] = useState({
    name: "",
    entity: "",
    currency: "INR",
    account_id: "",
  });

  const handleChange = (e) => {
    setAccountData({ ...accountData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(accountData);
    onClose(); // Close the modal after submission
  };

  return (
    <Form onSubmit={handleSubmit}>
      <Form.Group className="mb-3" controlId="formAccountName">
        <Form.Label>Account Name</Form.Label>
        <Form.Control
          type="text"
          name="name"
          value={accountData.name}
          onChange={handleChange}
          placeholder="Enter account name"
          required
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="formAccountId">
        <Form.Label>Account number</Form.Label>
        <Form.Control
          type="number"
          name="account_id"
          value={accountData.account_id}
          onChange={handleChange}
          placeholder="Enter account number"
          required
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="formAccountEntity">
        <Form.Label>Entity</Form.Label>
        <Form.Control
          as="select"
          name="entity"
          value={accountData.entity}
          onChange={handleChange}
          required
        >
          <option value="">Select entity</option>
          <option value="BANK">Bank</option>
          <option value="BROKER">Broker</option>
          <option value="EXCHANGE">Exchange</option>
        </Form.Control>
      </Form.Group>

      <Form.Group className="mb-3" controlId="formAccountCurrency">
        <Form.Label>Currency</Form.Label>
        <Form.Control
          type="text"
          name="currency"
          value={accountData.currency}
          onChange={handleChange}
          placeholder="Enter currency"
          required
        />
      </Form.Group>

      {/* <Form.Group className="mb-3" controlId="formCashBalance">
        <Form.Label>Cash Balance</Form.Label>
        <Form.Control
          type="number"
          name="cash_balance"
          value={accountData.cash_balance}
          onChange={handleChange}
          placeholder="Enter cash balance"
          required
        />
      </Form.Group> */}

      <Button variant="primary" type="submit">
        Add Account
      </Button>
    </Form>
  );
};

export default AccountForm;
