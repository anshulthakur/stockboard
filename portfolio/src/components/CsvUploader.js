import React, { useState } from 'react';
import { Button, Table, Form } from 'react-bootstrap';

const CsvUploader = ({ onSubmit, handleClose }) => {
    const [csvFile, setCsvFile] = useState(null);
    const [previewData, setPreviewData] = useState([]);
    const [errors, setErrors] = useState(null);

    const handleFileChange = (e) => {
        setCsvFile(e.target.files[0]);
    };

    const handlePreview = () => {
        if (!csvFile) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            const fileContent = event.target.result;
            const rows = fileContent.split('\n').map(row => row.split(','));

            if (rows.length && rows[0].length === 7) { // Example validation for 7 columns
                setPreviewData(rows);
                setErrors(null);
            } else {
                setErrors('CSV format is incorrect. Expected 7 columns.');
                setPreviewData([]);
            }
        };
        reader.readAsText(csvFile);
    };

    const handleSubmit = () => {
        if (previewData.length > 0) {
            onSubmit(previewData);
            handleClose(); // Close modal after submission
        } else {
            setErrors('Please preview the file before submitting.');
        }
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

            {errors && <div className="text-danger">{errors}</div>}

            {previewData.length > 0 && (
                <>
                    <h5 className="mt-4">Preview</h5>
                    <Table striped bordered hover responsive>
                        <thead>
                            <tr>
                                <th>Column 1</th>
                                <th>Column 2</th>
                                <th>Column 3</th>
                                <th>Column 4</th>
                                <th>Column 5</th>
                                <th>Column 6</th>
                                <th>Column 7</th>
                            </tr>
                        </thead>
                        <tbody>
                            {previewData.map((row, index) => (
                                <tr key={index}>
                                    {row.map((col, i) => (
                                        <td key={i}>{col}</td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </Table>
                    <Button variant="success" onClick={handleSubmit}>
                        Submit
                    </Button>
                </>
            )}
        </div>
    );
};

export default CsvUploader;
