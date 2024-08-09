// OrderBook.js
import React, { useState, useEffect } from 'react';
import Table from 'react-bootstrap/Table';
import SearchBar from './Layout/SearchBar';
import PaginationComponent from './Layout/Pagination';

import { orderData } from '../fixtures'; // Adjust the path as needed

const getRowClass = (type) => {
    return type === "buy" ? "table-success" : "table-warning"; // Green for buy, yellow for sell
};

const OrderBook = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [currentPage, setCurrentPage] = useState(1);

    const itemsPerPage = 10;

    const filteredOrders = orderData.filter(order =>
        order.symbol.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentItems = filteredOrders.slice(indexOfFirstItem, indexOfLastItem);

    return (
        <div>
            <h2>Orders</h2>
            <SearchBar placeholder="Search by symbol" searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
            <Table striped bordered hover responsive>
                <thead>
                    <tr>
                        <th>Ticker</th>
                        <th>Broker</th>
                        <th>Value Date</th>
                        <th>Shares</th>
                        <th>Price</th>
                        <th>Fee</th>
                        <th>Exchange Fee</th>
                        <th>Total</th>
                        <th>Cost</th>
                    </tr>
                </thead>
                <tbody>
                    {currentItems.map((order, index) => (
                        <tr key={index} className={getRowClass(order.type)}>
                            <td>{order.symbol}</td>
                            <td>{order.broker}</td>
                            <td>{order.valueDate}</td>
                            <td>{order.shares}</td>
                            <td>{order.price}</td>
                            <td>{order.fee}</td>
                            <td>{order.exchangeFee}</td>
                            <td>{order.total}</td>
                            <td>{order.cost}</td>
                        </tr>
                    ))}
                </tbody>
            </Table>
            <PaginationComponent
                itemsPerPage={itemsPerPage}
                totalItems={filteredOrders.length}
                currentPage={currentPage}
                setCurrentPage={setCurrentPage}
            />
        </div>
    );
};

export default OrderBook;