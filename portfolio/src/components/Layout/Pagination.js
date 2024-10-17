import React from 'react';
import Pagination from 'react-bootstrap/Pagination';

const PaginationComponent = ({ itemsPerPage, totalItems, currentPage, setCurrentPage }) => {
    const totalPages = Math.ceil(totalItems / itemsPerPage);

    const handleClick = (pageNumber) => {
        setCurrentPage(pageNumber);
    };

    const generatePaginationItems = () => {
        const items = [];

        if (totalPages <= 1) return items;

        items.push(
            <Pagination.Item 
                key={1} 
                active={1 === currentPage} 
                onClick={() => handleClick(1)}
            >
                1
            </Pagination.Item>
        );

        if (currentPage > 4) {
            items.push(<Pagination.Ellipsis key="start-ellipsis" />);
        }

        for (let i = Math.max(2, currentPage - 2); i <= Math.min(totalPages - 1, currentPage + 2); i++) {
            items.push(
                <Pagination.Item 
                    key={i} 
                    active={i === currentPage} 
                    onClick={() => handleClick(i)}
                >
                    {i}
                </Pagination.Item>
            );
        }

        if (currentPage < totalPages - 3) {
            items.push(<Pagination.Ellipsis key="end-ellipsis" />);
        }

        items.push(
            <Pagination.Item 
                key={totalPages} 
                active={totalPages === currentPage} 
                onClick={() => handleClick(totalPages)}
            >
                {totalPages}
            </Pagination.Item>
        );

        return items;
    };

    return (
        <Pagination>
            <Pagination.Prev 
                onClick={() => handleClick(currentPage - 1)} 
                disabled={currentPage === 1} 
            />
            {generatePaginationItems()}
            <Pagination.Next 
                onClick={() => handleClick(currentPage + 1)} 
                disabled={currentPage === totalPages} 
            />
        </Pagination>
    );
};

export default PaginationComponent;
