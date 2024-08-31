import React, { useContext, useState, useEffect } from "react";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import { AccountsContext } from "./AccountsContext";

const PortfolioForm = ({ onSubmit, onClose }) => {
  const { accounts } = useContext(AccountsContext);
  const [portfolioData, setPortfolioData] = useState({
    name: "",
    account:"",
  });

  const handleChange = (e) => {
    setPortfolioData({ ...portfolioData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
      e.preventDefault();
      onSubmit(portfolioData);
      onClose(); // Close the modal after submission
  };

  const brokerAccounts = accounts.filter(account => account.entity === 'BRKR');

  return (
    <Form onSubmit={handleSubmit}>
      <Form.Group className="mb-3" controlId="formPortfolioName">
        <Form.Label>Portfolio Name</Form.Label>
        <Form.Control
          type="text"
          name="name"
          value={portfolioData.name}
          onChange={handleChange}
          placeholder="Enter portfolio name"
          required
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="formLinkedBrokerAccount">
        <Form.Label>Linked Broker Account</Form.Label>
        <Form.Control
          as="select"
          name="account"
          value={portfolioData.account}
          onChange={handleChange}
        >
          <option value="">Select Broker</option>
          {brokerAccounts.map(account => (
            <option key={account.id} value={account.url}>
                {account.name}
            </option>
          ))}
        </Form.Control>
      </Form.Group>

      <Button variant="primary" type="submit">
        Create Portfolio
      </Button>
    </Form>
  );
};

export default PortfolioForm;
