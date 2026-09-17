import { useState } from 'react'
import './App.css'

function App() {
  const [city, setCity] = useState('')
  const [forecast, setForecast] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const getForecast = async () => {
    if (!city.trim()) return
    setLoading(true)
    setError(null)
    setForecast(null)

    try {
      const response = await fetch('http://127.0.0.1:8000/forecast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ city: city, days: 7 })
      })

      if (!response.ok) {
        throw new Error('City not found. Try a different spelling.')
      }

      const data = await response.json()
      setForecast(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: '700px', margin: '40px auto', fontFamily: 'sans-serif', padding: '0 20px' }}>
      <h1>🌤️ Weather Forecast</h1>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <input
          type="text"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && getForecast()}
          placeholder="Enter a city name..."
          style={{ flex: 1, padding: '10px', fontSize: '16px' }}
        />
        <button onClick={getForecast} style={{ padding: '10px 20px', fontSize: '16px' }}>
          {loading ? 'Loading...' : 'Get Forecast'}
        </button>
      </div>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {forecast && (
        <div>
          <h2>{forecast.city}, {forecast.country}</h2>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #333' }}>
                <th style={{ textAlign: 'left', padding: '8px' }}>Date</th>
                <th style={{ textAlign: 'left', padding: '8px' }}>Temp (°C)</th>
                <th style={{ textAlign: 'left', padding: '8px' }}>Rain Chance</th>
                <th style={{ textAlign: 'left', padding: '8px' }}>Wind (km/h)</th>
              </tr>
            </thead>
            <tbody>
              {forecast.forecast.map((day) => (
                <tr key={day.date} style={{ borderBottom: '1px solid #ddd' }}>
                  <td style={{ padding: '8px' }}>{day.date}</td>
                  <td style={{ padding: '8px' }}>{day.temperature}°C</td>
                  <td style={{ padding: '8px' }}>{Math.round(day.rain_probability * 100)}%</td>
                  <td style={{ padding: '8px' }}>{day.windspeed} km/h</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default App