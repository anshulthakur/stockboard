import React, { useContext, useState, useEffect } from "react";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import { AccountsContext } from "./AccountsContext";

const AccountForm = ({ onSubmit, onClose }) => {
  const { accounts } = useContext(AccountsContext);
  const [accountData, setAccountData] = useState({
    name: "",
    entity: "",
    currency: "INR",
    account_id: "",
    linked_demat_account: "",
    parent_account: ""
  });

  const handleChange = (e) => {
    setAccountData({ ...accountData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
      e.preventDefault();
      onSubmit(accountData);
      onClose(); // Close the modal after submission
  };

  const filteredDematAccounts = accounts.filter(account => account.entity === 'DMAT');
  const filteredBankAccounts = accounts.filter(account => account.entity === 'BANK');


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
          <option value="BRKR">Broker</option>
          <option value="DMAT">Demat</option>
          <option value="XCNG">Exchange</option>
          <option value="DPST">Deposit</option>
          <option value="SUB">Virtual account</option>
        </Form.Control>
      </Form.Group>

      {accountData.entity === "BRKR" && (
        <Form.Group className="mb-3" controlId="formLinkedDematAccount">
          <Form.Label>Linked Demat Account</Form.Label>
          <Form.Control
            as="select"
            name="linked_demat_account"
            value={accountData.linked_demat_account}
            onChange={handleChange}
          >
            <option value="">Select Demat Account</option>
            {filteredDematAccounts.map(account => (
              <option key={account.id} value={account.url}>
                  {account.name}
              </option>
            ))}
          </Form.Control>
        </Form.Group>
      )}

      {accountData.entity === "SUB" && (
        <Form.Group className="mb-3" controlId="formParentAccount">
          <Form.Label>Parent Account</Form.Label>
          <Form.Control
            as="select"
            name="parent_account"
            value={accountData.parent_account}
            onChange={handleChange}
          >
            <option value="">Select Parent Account</option>
            {filteredBankAccounts.map(account => (
              <option key={account.id} value={account.url}>
                  {account.name}
              </option>
            ))}
          </Form.Control>
        </Form.Group>
      )}

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

      <Button variant="primary" type="submit">
        Add Account
      </Button>
    </Form>
  );
};

export default AccountForm;
