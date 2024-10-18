import React, { useContext, useEffect } from "react";
import axios from "axios";
import { Table } from "react-bootstrap";
import { AccountsContext } from "../AccountsContext";

const Transactions = ({ account, transactions }) => {
  // const { accounts } = useContext(AccountsContext); // Access accounts data
  //   useEffect(() => {
  //     fetchTransactions(account);
  //   }, [account, fetchTransactions]);
  
    return (
      <Table responsive striped bordered hover>
        <thead>
          <tr>
            <th>ID</th>
            <th>Time</th>
            <th>Credit</th>
            <th>Debit</th>
            <th>Info</th>
          </tr>
        </thead>
        <tbody>
          {
            transactions.map((transaction, t_id) => {
              let credit = null;
              let debit = null;
              let notes = transaction.notes || "";
  
              if (transaction.transaction_type === "CR" || 
                  (transaction.transaction_type === "TR" && transaction.destination_account.endsWith(`${account.id}/`))) {
                credit = transaction.amount;
                notes += " (from external)";
                if (transaction.transaction_type === "TR") {
                  notes = ` (from <a href="${transaction.source_account}">source</a>)`;
                }
              } else {
                debit = transaction.amount;
                notes += " (to external)";
                if (transaction.transaction_type === "TR") {
                  notes = ` (to <a href="${transaction.destination_account}">destination</a>)`;
                }
              }
  
              return (
                <tr key={t_id} className={credit ? "table-success" : "table-danger"}>
                  <td>{transaction.transaction_id}</td>
                  <td>{new Date(transaction.timestamp).toLocaleString()}</td>
                  <td>{credit ? credit : ""}</td>
                  <td>{debit ? debit : ""}</td>
                  <td dangerouslySetInnerHTML={{ __html: notes }} />
                </tr>
              );
            })
          }
        </tbody>
      </Table>
    );
};
  
export default Transactions;
