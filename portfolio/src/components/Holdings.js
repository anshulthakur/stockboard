import React, { useState, useEffect } from 'react';
import SearchBar from './Layout/SearchBar';
import PaginationComponent from './Layout/Pagination';
import { Table } from "react-bootstrap";

const Holdings = ({ portfolio, holdings }) => {

    return (
        <Table responsive striped bordered hover>
          <thead>
            <tr>
                <th>Company</th>
                <th>Symbol</th>
                <th>Shares</th>
                <th>Price</th>
                <th>Cost</th>
                <th>Current Price</th>
                <th>Value</th>
                <th>W/L</th>
                <th>Day Change</th>
            </tr>
          </thead>
          <tbody>
          {holdings.map(item => (
              <tr key={item.symbol}>
                <td>{item.stock}</td>
                <td>{item.symbol}</td>
                <td>{item.shares}</td>
                <td>{item.price}</td>
                <td>{item.cost}</td>
                <td>{item.currentPrice}</td>
                <td>{item.value}</td>
                <td>{item.wl}</td>
                <td>{item.dayChange}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      );
};

export default Holdings;