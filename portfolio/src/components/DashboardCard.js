import React from 'react';
import Card from 'react-bootstrap/Card';
import 'bootstrap/dist/css/bootstrap.min.css';

const DashboardCard = ({ title, value, subtitle, icon }) => {
    return (
        <Card className="text-center mb-3">
            <Card.Body>
                <div className="d-flex align-items-center justify-content-center mb-2">
                    <i className={`fa ${icon} fa-2x`}></i>
                </div>
                <Card.Title>{title}</Card.Title>
                <div>
                    <h3>{value}</h3>
                    {subtitle && <p>{subtitle}</p>}
                </div>
            </Card.Body>
        </Card>
    );
};

export default DashboardCard;
