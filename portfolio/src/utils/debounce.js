import React, { useContext, useState, useCallback } from 'react';

function useDebounce(callback, delay) {
    const timeoutRef = React.useRef(null);
  
    const debounceFn = (...args) => {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = setTimeout(() => {
        callback(...args);
      }, delay);
    };
  
    return debounceFn;
  }

export default useDebounce;