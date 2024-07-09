import React from 'react';
import Table from 'react-bootstrap/Table';

var account_transactions = [
    {
      datetime: '12-June-2024 12:00 IST',
      credit: 1000,
      debit: 0,
      info: 'Pay in'
    },
    {
      datetime: '12-June-2024 14:00 IST',
      credit: 0,
      debit: 597,
      info: 'Stonks'
    },
  ];

const Transactions = ({account_id}) => {
    let transactions = account_transactions;

    return (
        <Table responsive striped bordered hover>
            <thead>
            <tr>
                <th>S.No.</th>
                <th>Time</th>
                <th>Info</th>
                <th>Debit</th>
                <th>Credit</th>
            </tr>
            </thead>
            <tbody>
            {transactions.map((transaction, t_id) => (
                <tr key={t_id}>
                    <td>{t_id}</td>
                    <td>{transaction.datetime}</td>
                    <td>{transaction.info}</td>
                    <td>{transaction.debit}</td>
                    <td>{transaction.credit}</td>
                </tr>
            ))}
            </tbody>
        </Table>
    );
};

export default Transactions;