import React, { useContext, useEffect } from "react";
import { Table } from "react-bootstrap";

const getRowClass = (type) => {
  return type === "buy" ? "table-success" : "table-warning"; // Green for buy, yellow for sell
};

const Trades = ({ portfolio, trades, fetchTrades }) => {
    useEffect(() => {
      fetchTrades(portfolio.id);
    }, [portfolio, fetchTrades]);
  
    return (
      <Table responsive striped bordered hover>
        <thead>
          <tr>
              <th>Trade ID</th>
              <th>Date</th>
              <th>Ticker</th>
              <th>Operation</th>
              <th>Quantity</th>
              <th>Price</th>
              <th>Tax</th>
              <th>Brokerage</th>
              <th>Trade Value</th>
          </tr>
        </thead>
        <tbody>
        {trades.map((trade, index) => (
              <tr key={index} className={getRowClass(trade.operation)}>
                  <td>{trade.id}</td>
                  <td>{new Date(trade.timestamp).toLocaleString()}</td>
                  <td>{trade.stock}</td>
                  <td>{trade.operation}</td>
                  <td>{trade.quantity}</td>
                  <td>{trade.price}</td>
                  <td>{trade.tax}</td>
                  <td>{trade.brokerage}</td>
                  <td>{parseFloat(trade.quantity) * parseFloat(trade.price)}</td>
              </tr>
          ))}
        </tbody>
      </Table>
    );
};
  
export default Trades;
