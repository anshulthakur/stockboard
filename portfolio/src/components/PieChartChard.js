import React from 'react';
import Card from 'react-bootstrap/Card';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const PieChartCard = ({ title, data }) => {
    const COLORS = ['#FF6384', '#36A2EB', '#FFCE56'];

    const chartData = data.labels.map((label, index) => ({
        name: label,
        value: data.values[index],
    }));

    return (
        <Card className="text-center mb-3">
            <Card.Body>
                <Card.Title>{title}</Card.Title>
                <div style={{ width: '100%', height: 300 }}>
                    <ResponsiveContainer>
                        <PieChart>
                            <Pie
                                data={chartData}
                                cx="50%"
                                cy="50%"
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="value"
                                label
                            >
                                {chartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip />
                            <Legend layout="horizontal" align="center" />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </Card.Body>
        </Card>
    );
};

export default PieChartCard;
