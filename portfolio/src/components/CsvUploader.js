import React, { useState } from 'react';
import { Button, Table, Form } from 'react-bootstrap';

const CsvUploader = ({ onSubmit, handleClose, currentPortfolio }) => {
    const [csvFile, setCsvFile] = useState(null);
    const [previewData, setPreviewData] = useState([]);
    const [errors, setErrors] = useState(null);
    const [tradeErrors, setTradeErrors] = useState([]); // Store errors per trade row

    const expectedHeaders = [
        { label: 'Trade ID', key: 'trade_id' },
        { label: 'Exchange', key: 'exchange' },
        { label: 'Datetime', key: 'timestamp' },
        { label: 'ISIN', key: 'isin' },
        { label: 'Security', key: 'name' },
        { label: 'Buy/Sell', key: 'operation' },
        { label: 'Quantity', key: 'quantity' },
        { label: 'Price', key: 'price' },
        { label: 'Brokerage', key: 'brokerage' },
        { label: 'Service Tax', key: 'tax' },
    ];

    const handleFileChange = (e) => {
        setCsvFile(e.target.files[0]);
    };

    const formatTimestamp = (timestamp) => {
        const [date, time] = timestamp.split(' ');
        const [day, month, year] = date.split('-');
        const formattedTimestamp = `${year}-${month}-${day}T${time}:00`;
        return new Date(formattedTimestamp).toISOString().slice(0, 19);
    };

    const formatOperation = (operation) => {
        if (operation === 'B') return 'BUY';
        if (operation === 'S') return 'SELL';
        return operation;
    };

    const handlePreview = () => {
        if (!csvFile) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            const fileContent = event.target.result;
            const rows = fileContent.trim().split('\n').map(row => row.split(','));

            if (rows.length > 0) {
                const headers = rows[0].map(header => header.trim());

                if (headers.join(',') === expectedHeaders.map(h => h.label).join(',')) {
                    const formattedPreview = rows.slice(1).map((row, idx) => ({
                        trade_id: row[0],
                        exchange: row[1],
                        timestamp: formatTimestamp(row[2]),
                        isin: row[3],
                        name: row[4],
                        operation: formatOperation(row[5]),
                        quantity: row[6],
                        price: row[7],
                        brokerage: row[8],
                        tax: row[9],
                        portfolio: currentPortfolio.url,
                        error: null, // Placeholder for individual trade errors
                    }));
                    setPreviewData(formattedPreview);
                    setErrors(null);
                } else {
                    setErrors('CSV header is incorrect. Please ensure the headers match the expected format.');
                    setPreviewData([]);
                }
            } else {
                setErrors('CSV file is empty or not in the correct format.');
                setPreviewData([]);
            }
        };
        reader.readAsText(csvFile);
    };

    const handleFieldChange = (index, field, value) => {
        setPreviewData(prev => {
            const updatedData = [...prev];
            updatedData[index][field] = value;
            return updatedData;
        });
    };

    const handleDeleteRow = (index) => {
        setPreviewData(prev => prev.filter((_, i) => i !== index));
    };

    const handleSubmit = async () => {
        if (previewData.length > 0) {
            try {
                const response = await fetch('/portfolio/api/bulk-trades/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken, // Assumes `csrftoken` is available globally
                    },
                    body: JSON.stringify(previewData),
                });

                if (response.ok) {
                    const data = await response.json();
                    onSubmit(data);
                    handleClose();
                } else {
                    const errorData = await response.json();
                    setTradeErrors(errorData);
                }
            } catch (error) {
                setErrors(`Failed to upload: ${error.message}`);
            }
        } else {
            setErrors('Please preview the file before submitting.');
        }
    };

    // Utility function to check if an object is empty
    const isEmptyObject = (obj) => {
        return Object.keys(obj).length === 0;
    };

    return (
        <div>
            <Form.Group>
                <Form.Label>Upload CSV File</Form.Label>
                <Form.Control type="file" onChange={handleFileChange} />
            </Form.Group>
            <Button variant="primary" onClick={handlePreview}>
                Preview
            </Button>

            {errors && <div className="text-danger mt-2">{errors}</div>}

            {previewData.length > 0 && (
                <>
                    <h5 className="mt-4">Preview</h5>
                    <Table striped bordered hover responsive>
                        <thead>
                            <tr>
                                {expectedHeaders.map((header, index) => (
                                    <th key={index}>{header.label}</th>
                                ))}
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {previewData.map((trade, index) => (
                                <React.Fragment key={index}>
                                    <tr
                                        className={
                                            tradeErrors[index]
                                                ? isEmptyObject(tradeErrors[index])
                                                    ? 'table-success' // Green for no errors
                                                    : 'table-danger' // Red for errors
                                                : ''
                                        }
                                    >
                                        {expectedHeaders.map(({ key }, i) => (
                                            <td key={i}>
                                                <Form.Control
                                                    type="text"
                                                    value={trade[key]}
                                                    onChange={(e) => handleFieldChange(index, key, e.target.value)}
                                                    isInvalid={!!(tradeErrors[index] && tradeErrors[index][key])}
                                                />
                                                {tradeErrors[index] && tradeErrors[index][key] && (
                                                    <Form.Control.Feedback type="invalid">
                                                        {tradeErrors[index][key].join(', ')}
                                                    </Form.Control.Feedback>
                                                )}
                                            </td>
                                        ))}
                                        <td>
                                            <Button
                                                variant="danger"
                                                onClick={() => handleDeleteRow(index)}
                                            >
                                                Delete
                                            </Button>
                                        </td>
                                    </tr>
                                    {tradeErrors[index] && tradeErrors[index].non_field_errors && (
                                        <tr className="text-danger">
                                            <td colSpan={expectedHeaders.length + 1}>
                                                {tradeErrors[index].non_field_errors.join(', ')}
                                            </td>
                                        </tr>
                                    )}
                                </React.Fragment>
                            ))}
                        </tbody>
                    </Table>
                    <Button variant="success" className="mt-2" onClick={handleSubmit}>
                        Submit
                    </Button>
                </>
            )}
        </div>
    );
};

export default CsvUploader;
