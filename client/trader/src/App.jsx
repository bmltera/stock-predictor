import { useState } from 'react'
import './App.css'

function App() {
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])
  const [dateMessage, setDateMessage] = useState("")
  const [highPrice, setHighPrice] = useState()
  const [lowPrice, setLowPrice] = useState()
  const [avgPrice, setAvgPrice] = useState()
  const [tradingStrategy, setTradingStrategy] = useState([])
  const [loading, setLoading] = useState(false)


  const fetchData = async () => {
    setLoading(true)
    try {

      // dummy data DELETE LATER
      setHighPrice(getRandomPrice());
      setLowPrice(getRandomPrice());
      setAvgPrice(getRandomPrice());
      setTradingStrategy([
        ["2023-10-01", "BEAR"],
        ["2023-10-01", "BULL"],
        ["2023-10-01", "BEAR"],
        ["2023-10-01", "BULL"],
        ["2023-10-01", "BULL"]
      ]);

      const response = await fetch(`http://localhost:8000/predict?date=${date}`)
      const result = await response.json();
      setHighPrice(result.high)
      setLowPrice(result.low)
      setAvgPrice(result.avg)
      setTradingStrategy(result.strategy)

    }
    catch (error) {
      console.error("Error fetching data:", error)
    }
    finally {
      setLoading(false)
    }
  }
  
  const getRandomPrice = () => {
    return (Math.random() * (200 - 10) + 10).toFixed(2); // Generates a random price between 10.00 and 200.00
  };

  const resetData = () => {
    setHighPrice(null)
    setLowPrice(null)
    setAvgPrice(null)
    setTradingStrategy(null)
  }
  
  return (
    <>
      <h1>SmartTrader Console</h1>
      <div className="top-container"> 
        <p>Assume today's date is:</p>
        <input 
          type="date" 
          value={date} 
          onChange={(e) => setDate(e.target.value)} 
        />
        <button onClick={fetchData}>Predict</button>
      </div>
      
      <div className="bottom-container">
        {loading && <p>Loading...</p>} {/* Show loading indicator */}
        {!loading && 
          <>
        <h3 style={{ textAlign: 'left' }}>Predicted prices for the next five business days in USD are:</h3>
        <table style={{ border: '1px solid black', borderCollapse: 'collapse' }}>
          <tbody>
            <tr>
              <td style={{ border: '1px solid black' }}>Highest Price</td>
              <td style={{ border: '1px solid black' }}>{highPrice}</td>
            </tr>
            <tr>
              <td style={{ border: '1px solid black' }}>Lowest Price</td>
              <td style={{ border: '1px solid black' }}>{lowPrice}</td>
            </tr>
            <tr>
              <td style={{ border: '1px solid black' }}>Average Closing Price</td>
              <td style={{ border: '1px solid black' }}>{avgPrice}</td>
            </tr>
          </tbody>
        </table>
        <h3 style={{ textAlign: 'left' }}>Recomended trading strategy:</h3>
        <table style={{ border: '1px solid black', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ border: '1px solid black' }}>Date</th>
                <th style={{ border: '1px solid black' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {tradingStrategy.map((tuple, index) => (
                <tr key={index}>
                  <td style={{ border: '1px solid black' }}>{tuple[0]}</td>
                  <td style={{ border: '1px solid black' }}>{tuple[1]}</td>
                </tr>
              ))}
            </tbody>
          </table>

          </>
        }
      </div>
    </>
  )
}

export default App