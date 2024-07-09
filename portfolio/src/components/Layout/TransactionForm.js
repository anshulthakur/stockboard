import React from 'react';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';

function TransactionForm() {
    return (
      <Form>
        <Form.Group className="mb-3" controlId="tf-amount">
          <Form.Label>Amount</Form.Label>
          <Form.Control type="number" step="0.001" placeholder="0" />
        </Form.Group>
  
        <Form.Group className="mb-3" controlId="tf-type">
          <Form.Label>Type</Form.Label>
          <Form.Select aria-label="Credit or Debit">
            <option value="DB">Debit</option>
            <option value="CR">Credit</option>
          </Form.Select>
        </Form.Group>

        <Form.Group className="mb-3" controlId="tf-info">
          <Form.Control type="text" label="Transaction information" />
        </Form.Group>

        <Button variant="primary" type="submit">
          Add
        </Button>
      </Form>
    );
  }
  
  export default TransactionForm;