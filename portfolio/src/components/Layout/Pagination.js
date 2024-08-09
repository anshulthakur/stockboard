// PaginationComponent.js
import React from 'react';
import Pagination from 'react-bootstrap/Pagination';

const PaginationComponent = ({ itemsPerPage, totalItems, currentPage, setCurrentPage }) => {
    const totalPages = Math.ceil(totalItems / itemsPerPage);

    const handleClick = (pageNumber) => {
        setCurrentPage(pageNumber);
    };

    return (
        <Pagination>
            <Pagination.Prev 
                onClick={() => handleClick(currentPage - 1)} 
                disabled={currentPage === 1} 
            />
            {[...Array(totalPages)].map((_, index) => (
                <Pagination.Item
                    key={index}
                    active={index + 1 === currentPage}
                    onClick={() => handleClick(index + 1)}
                >
                    {index + 1}
                </Pagination.Item>
            ))}
            <Pagination.Next 
                onClick={() => handleClick(currentPage + 1)} 
                disabled={currentPage === totalPages} 
            />
        </Pagination>
    );
};

export default PaginationComponent;
