// fixtures.js

export const stockWalletData = {
  summary: {
    cost: "₹7,549.00",
    walletValue: "₹0.00",
    previousDay: "₹0.00",
    currentWL: "-₹6,069.00",
    materializedWL: "₹1,494.00"
  },
  entries: [
    {
      symbol: "TSLA",
      shares: 15,
      price: "₹502.87",
      cost: "₹7,543.00",
      be: "₹371.01",
      currentPrice: "₹0.00",
      value: "₹7,543.00",
      wl: "-₹6,069.00",
      dayChange: "₹0.00",
      preChange: "₹0.00"
    },
    {
      symbol: "TATASTEEL",
      shares: 15,
      price: "₹502.87",
      cost: "₹7,543.00",
      be: "₹371.01",
      currentPrice: "₹0.00",
      value: "₹7,543.00",
      wl: "-₹6,069.00",
      dayChange: "₹0.00",
      preChange: "₹0.00"
    }
    // Add more entries as needed
  ]
};
  
export const cryptoWalletData = {
  summary: {
    cost: "₹3,200.00",
    walletValue: "₹1,200.00",
    previousDay: "₹1,500.00",
    currentWL: "-₹1,000.00",
    materializedWL: "₹200.00"
  },
  entries: [
    {
      symbol: "BTC",
      shares: 2,
      price: "₹30,000.00",
      cost: "₹60,000.00",
      be: "₹25,000.00",
      currentPrice: "₹35,000.00",
      value: "₹70,000.00",
      wl: "₹10,000.00",
      dayChange: "₹500.00",
      preChange: "₹-200.00"
    }
    // Add more entries as needed
  ]
};
  
export const orderData = [
  {
      symbol: "TSLA",
      broker: "Degiro acc",
      valueDate: "2021-02-02",
      shares: 10,
      price: "$600.00",
      fee: "-€3.00",
      exchangeFee: "-€1.00",
      total: "$6,000.00",
      cost: "€5,996.00",
      type: "buy" // buy or sell
  },
  {
      symbol: "TSLA",
      broker: "Degiro acc",
      valueDate: "2021-02-01",
      shares: 5,
      price: "$600.00",
      fee: "-€3.00",
      exchangeFee: "-€1.00",
      total: "$3,000.00",
      cost: "€2,996.00",
      type: "sell"
  },
  // Add more orders
];