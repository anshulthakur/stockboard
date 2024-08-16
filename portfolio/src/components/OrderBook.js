import React, { useState } from 'react';
import { Button, Modal, Row, Col, Table } from 'react-bootstrap';
import SearchBar from './Layout/SearchBar';
import PaginationComponent from './Layout/Pagination';
import TradeForm from './TradeForm';
import CsvUploader from './CsvUploader'; // Import the CsvUpload component
import { orderData } from '../fixtures'; // Adjust the path as needed

const getRowClass = (type) => {
    return type === "buy" ? "table-success" : "table-warning"; // Green for buy, yellow for sell
};

const OrderBook = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [showModal, setShowModal] = useState(false);
    const [showCsvModal, setShowCsvModal] = useState(false); // New state for CSV modal

    const handleShow = () => setShowModal(true);
    const handleClose = () => setShowModal(false);
    const handleCsvShow = () => setShowCsvModal(true); // Function to show CSV modal
    const handleCsvClose = () => setShowCsvModal(false); // Function to close CSV modal

    const itemsPerPage = 10;

    const filteredOrders = orderData.filter(order =>
        order.symbol.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentItems = filteredOrders.slice(indexOfFirstItem, indexOfLastItem);

    const handleCsvSubmit = (data) => {
        console.log('CSV data submitted:', data);
        // Handle bulk creation of trades with submitted data
        // You can make an API call here to create trades in bulk
    };

    return (
        <div>
            <h2>Orders</h2>
            <Row className="p-3">
                <Col md={6}>
                    <SearchBar searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
                </Col>
                <Col md={3}>
                    <Button variant="primary" onClick={handleShow}>
                        Add Trade
                    </Button>
                </Col>
                <Col md={3}>
                    <Button variant="secondary" onClick={handleCsvShow}>
                        Upload
                    </Button>
                </Col>
            </Row>            
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
            <Modal show={showModal} onHide={handleClose}>
                <Modal.Header closeButton>
                    <Modal.Title>Add a New Trade</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <TradeForm handleClose={handleClose} />
                </Modal.Body>
            </Modal>
            <Modal show={showCsvModal} onHide={handleCsvClose} size="xl">
                <Modal.Header closeButton>
                    <Modal.Title>Upload CSV</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <CsvUploader onSubmit={handleCsvSubmit} handleClose={handleCsvClose} />
                </Modal.Body>
            </Modal>
        </div>
    );
};

export default OrderBook;
