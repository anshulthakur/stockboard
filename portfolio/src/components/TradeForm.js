import React, { useState } from 'react';
import { Form, Button } from 'react-bootstrap';
import axios from 'axios';

const TradeForm = ({ handleClose }) => {
  const [formData, setFormData] = useState({
    stock: '',
    quantity: '',
    price: '',
    operation: 'BUY',
    timestamp: new Date().toISOString(),
    portfolio: '',  // Set default portfolio or fetch list if needed
    tax: 0,
    brokerage: 0,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log(formData);
    handleClose();
    // try {
    //   await axios.post('/api/trades/', formData);
    //   handleClose();  // Close the modal after submission
    // } catch (error) {
    //   console.error('Error adding trade:', error);
    // }
  };

  return (
    <Form onSubmit={handleSubmit}>
      <Form.Group controlId="stock">
        <Form.Label>Stock</Form.Label>
        <Form.Control 
          type="text" 
          name="stock" 
          value={formData.stock} 
          onChange={handleChange} 
          placeholder="Enter stock symbol" 
        />
      </Form.Group>

      <Form.Group controlId="quantity">
        <Form.Label>Quantity</Form.Label>
        <Form.Control 
          type="number" 
          name="quantity" 
          value={formData.quantity} 
          onChange={handleChange} 
          placeholder="Enter quantity" 
        />
      </Form.Group>

      <Form.Group controlId="price">
        <Form.Label>Price</Form.Label>
        <Form.Control 
          type="number" 
          name="price" 
          value={formData.price} 
          onChange={handleChange} 
          placeholder="Enter price" 
        />
      </Form.Group>

      <Form.Group controlId="operation">
        <Form.Label>Operation</Form.Label>
        <Form.Control 
          as="select" 
          name="operation" 
          value={formData.operation} 
          onChange={handleChange}>
          <option value="BUY">BUY</option>
          <option value="SELL">SELL</option>
        </Form.Control>
      </Form.Group>

      <Form.Group controlId="tax">
        <Form.Label>Tax</Form.Label>
        <Form.Control 
          type="number" 
          name="tax" 
          value={formData.tax} 
          onChange={handleChange} 
          placeholder="Enter tax" 
        />
      </Form.Group>

      <Form.Group controlId="brokerage">
        <Form.Label>Brokerage</Form.Label>
        <Form.Control 
          type="number" 
          name="brokerage" 
          value={formData.brokerage} 
          onChange={handleChange} 
          placeholder="Enter brokerage fee" 
        />
      </Form.Group>

      <Button variant="primary" type="submit">
        Submit
      </Button>
    </Form>
  );
};

export default TradeForm;
