// components/Distribution.js
import React from 'react';
import Card from 'react-bootstrap/Card';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Distribution = ({ type, data }) => {
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  const pieData = data.entries.map(entry => ({
    name: entry.symbol,
    value: parseFloat(entry.value.replace(/[^\d.-]/g, '')) // Parse the value string to a float
  }));

  return (
    <div>
      <Card className="text-center mb-3">
            <Card.Body>
                <Card.Title>{type.charAt(0).toUpperCase() + type.slice(1)} Distribution</Card.Title>
                <div style={{ width: '100%', height: 300 }}>
                    <ResponsiveContainer>
                        <PieChart>
                            <Pie
                                data={pieData}
                                cx="50%"
                                cy="50%"
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="value"
                                label
                            >
                                {pieData.map((entry, index) => (
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
    </div>
  );
}

export default Distribution;
