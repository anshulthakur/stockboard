import React, { useContext, useEffect } from "react";
import { Table } from "react-bootstrap";

const getRowClass = (type) => {
  return type === "buy" ? "table-success" : "table-warning"; // Green for buy, yellow for sell
};

const Trades = ({ portfolio, trades}) => {
    // useEffect(() => {
    //   console.log('Render trades for portfolio ', portfolio.id);
    //   console.log(trades);
    //   fetchTrades(portfolio.id);
    // }, [portfolio, fetchTrades]);

    return (
      <div style={{ overflowX: 'auto', maxWidth: '100%', whiteSpace: 'nowrap' }}>
      <Table responsive striped bordered hover>
        <thead>
          <tr>
              <th>Trade ID</th>
              <th>Date</th>
              <th>Symbol</th>
              <th>Exchange</th>
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
                  <td>{trade.trade_id}</td>
                  <td>{new Date(trade.timestamp).toLocaleString()}</td>
                  <td><a href={trade.stock}>{trade.symbol}</a></td>
                  <td>{trade.market}</td>
                  <td>{trade.operation}</td>
                  <td>{trade.quantity}</td>
                  <td>{trade.price}</td>
                  <td>{trade.tax}</td>
                  <td>{trade.brokerage}</td>
                  <td>{(parseFloat(trade.quantity) * parseFloat(trade.price)).toFixed(2)}</td>
              </tr>
          ))}
        </tbody>
      </Table>
      </div>
    );
};
  
export default Trades;
