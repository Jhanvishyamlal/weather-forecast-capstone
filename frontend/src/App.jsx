import { useState, useEffect } from 'react'
import './App.css'

// =========================================================
// WEATHER CONDITION
// =========================================================

function getCondition(day) {
  if (!day) return 'default'

  const code = Number(day.weather_code)
  const rain = Number(day.rain || 0)
  const showers = Number(day.showers || 0)

  // Clear sky
  if (code === 0) return 'sunny'

  // Mainly clear
  if (code === 1) return 'sunny'

  // Partly cloudy
  if (code === 2) return 'partly-cloudy'

  // Overcast
  if (code === 3) return 'cloudy'

  // Fog
  if (code === 45 || code === 48) return 'foggy'

  // -------------------------------------------------------
  // DRIZZLE
  // -------------------------------------------------------
  // Do not show drizzle/rain animation for tiny
  // precipitation values such as 0.1 mm.
  if ([51, 53, 55, 56, 57].includes(code)) {
    if (rain >= 0.5 || showers >= 0.5) {
      return 'drizzle'
    }

    return 'partly-cloudy'
  }

  // -------------------------------------------------------
  // RAIN
  // -------------------------------------------------------
  if ([61, 63, 65, 66, 67].includes(code)) {
    return 'rainy'
  }

  // Rain showers
  if ([80, 81, 82].includes(code)) {
    return 'rainy'
  }

  // -------------------------------------------------------
  // SNOW
  // -------------------------------------------------------
  if ([71, 73, 75, 77, 85, 86].includes(code)) {
    return 'snowy'
  }

  // -------------------------------------------------------
  // THUNDERSTORM
  // -------------------------------------------------------
  if ([95, 96, 99].includes(code)) {
    return 'stormy'
  }

  return 'default'
}

// =========================================================
// CONDITION LABEL
// =========================================================

function getConditionLabel(condition) {
  const labels = {
    sunny: 'Sunny',
    'partly-cloudy': 'Partly Cloudy',
    cloudy: 'Cloudy',
    rainy: 'Rainy',
    drizzle: 'Drizzle',
    snowy: 'Snowy',
    stormy: 'Thunderstorm',
    foggy: 'Foggy',
    default: 'Weather'
  }

  return labels[condition] || 'Weather'
}

// =========================================================
// WEATHER ICON
// =========================================================

function getWeatherIcon(condition) {
  const icons = {
    sunny: '☀️',
    'partly-cloudy': '🌤️',
    cloudy: '☁️',
    rainy: '🌧️',
    drizzle: '🌦️',
    snowy: '❄️',
    stormy: '⛈️',
    foggy: '🌫️',
    default: '🌤️'
  }

  return icons[condition] || '🌤️'
}

// =========================================================
// RAIN PROBABILITY
// =========================================================

function getRainProbability(value) {
  const number = Number(value)

  if (!Number.isFinite(number)) return 0

  if (number < 0) return 0

  if (number > 100) return 100

  // Backend may return 0.45 instead of 45
  if (number > 0 && number < 1) {
    return Math.round(number * 100)
  }

  return Math.round(number)
}

// =========================================================
// FORMAT DATE
// =========================================================

function formatDate(dateString) {
  if (!dateString) return ''

  const date = new Date(dateString)

  if (Number.isNaN(date.getTime())) {
    return dateString
  }

  return date.toLocaleDateString('en-IN', {
    weekday: 'short',
    day: 'numeric',
    month: 'short'
  })
}

// =========================================================
// WEATHER ANIMATION
// =========================================================

function WeatherEffects({ condition }) {
  // Sunny
  if (condition === 'sunny') {
    return (
      <div className="weather-fx">
        <div className="sun"></div>
      </div>
    )
  }

  // Rain / drizzle
  if (condition === 'rainy' || condition === 'drizzle') {
    return (
      <div className="weather-fx rain">
        {Array.from({ length: 35 }).map((_, index) => (
          <div
            className="drop"
            key={index}
            style={{ '--i': index }}
          />
        ))}
      </div>
    )
  }

  // Snow
  if (condition === 'snowy') {
    return (
      <div className="weather-fx snow">
        {Array.from({ length: 25 }).map((_, index) => (
          <div
            className="flake"
            key={index}
            style={{ '--i': index }}
          >
            ❄
          </div>
        ))}
      </div>
    )
  }

  // Clouds
  if (
    condition === 'cloudy' ||
    condition === 'partly-cloudy' ||
    condition === 'foggy'
  ) {
    return (
      <div className="weather-fx clouds">
        <div className="cloud c1"></div>
        <div className="cloud c2"></div>
        <div className="cloud c3"></div>
      </div>
    )
  }

  return null
}

// =========================================================
// MAIN APP
// =========================================================

function App() {
  const [city, setCity] = useState('Chennai')
  const [forecast, setForecast] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showAlerts, setShowAlerts] = useState(false)

  // =======================================================
  // GET FORECAST
  // =======================================================

  const fetchForecast = async (cityName) => {
    const trimmedCity = cityName.trim()

    if (!trimmedCity) {
      setError('Please enter a city name.')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/forecast?city=${encodeURIComponent(trimmedCity)}&days=7`
      )

      if (!response.ok) {
        let message = `Server error: ${response.status}`

        try {
          const errorData = await response.json()

          if (errorData.detail) {
            message = errorData.detail
          }
        } catch {}

        throw new Error(message)
      }

      const data = await response.json()

      console.log('Forecast API response:', data)

      setForecast(data)

    } catch (err) {
      console.error('Forecast error:', err)

      setError(
        err.message || 'Unable to fetch weather data.'
      )

      setForecast(null)

    } finally {
      setLoading(false)
    }
  }

  // =======================================================
  // SEARCH BUTTON
  // =======================================================

  const getForecast = () => {
    fetchForecast(city)
  }

  // =======================================================
  // ENTER KEY
  // =======================================================

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      getForecast()
    }
  }

  // =======================================================
  // QUICK CITY
  // =======================================================

  const searchCity = (name) => {
    setCity(name)
    fetchForecast(name)
  }

  // =======================================================
  // CURRENT WEATHER
  // =======================================================

  const current = forecast?.current || null

  const currentCondition = current
    ? getCondition(current)
    : 'default'

  const currentConditionLabel =
    getConditionLabel(currentCondition)

  const currentIcon =
    getWeatherIcon(currentCondition)

  // =======================================================
  // CURRENT VALUES
  // =======================================================

  const currentTemperature =
    current?.temperature !== undefined &&
    current?.temperature !== null
      ? Number(current.temperature).toFixed(1)
      : '--'

  const currentHumidity =
    current?.humidity !== undefined &&
    current?.humidity !== null
      ? Math.round(Number(current.humidity))
      : '--'

  const currentWind =
    current?.windspeed !== undefined &&
    current?.windspeed !== null
      ? Number(current.windspeed).toFixed(1)
      : '--'

  const currentRain =
    current?.rain !== undefined &&
    current?.rain !== null
      ? Number(current.rain).toFixed(1)
      : '0.0'

  const currentPrecipitation =
    current?.precipitation !== undefined &&
    current?.precipitation !== null
      ? Number(current.precipitation).toFixed(1)
      : '0.0'

  // =======================================================
  // FORECAST
  // =======================================================

  const forecastDays =
    Array.isArray(forecast?.forecast)
      ? forecast.forecast
      : []

  // =======================================================
  // WEATHER TIP
  // =======================================================

  const weatherTip =
    forecast?.weather_tip || ''

  // =======================================================
  // SAFE ALERTS
  // =======================================================

  const rawAlerts =
    Array.isArray(forecast?.alerts)
      ? forecast.alerts
      : []

  // Remove fake flood / landslide alerts
  // because our current backend does not have a
  // real hazard-warning data source.

  const alerts = rawAlerts.filter((alert) => {
    const text =
      typeof alert === 'string'
        ? alert
        : alert?.message ||
          alert?.title ||
          ''

    const lower = text.toLowerCase()

    return (
      !lower.includes('flood') &&
      !lower.includes('landslide')
    )
  })

  // =======================================================
  // BACKGROUND
  // =======================================================

  const backgroundClass =
    `bg-${currentCondition}`

  // =======================================================
  // RENDER
  // =======================================================

  return (
    <div className={`weather-app ${backgroundClass}`}>

      <WeatherEffects
        condition={currentCondition}
      />

      {/* =================================================
          TOP NAV
      ================================================= */}

      <nav className="top-nav">

        <div className="brand">

          <div className="brand-icon">
            🌤️
          </div>

          <div className="brand-text">

            <div className="brand-name">
              Weather Forecast
            </div>

            <div className="brand-subtitle">
              AI Weather Intelligence
            </div>

          </div>

        </div>

        <button
          className="alerts-button"
          onClick={() => setShowAlerts(true)}
        >
          ⚠️ Alerts

          {alerts.length > 0 && (
            <span className="alert-count">
              {alerts.length}
            </span>
          )}

        </button>

      </nav>

      {/* =================================================
          MAIN CONTENT
      ================================================= */}

      <div className="content">

        {/* =================================================
            HERO
        ================================================= */}

        <section className="hero-section">

          <div className="hero-badge">
            AI POWERED FORECAST
          </div>

          <h1>
            Weather that
            <br />
            <span className="hero-highlight">
              looks ahead.
            </span>
          </h1>

          <p className="hero-subtitle">
            Get real-time weather conditions and
            AI-powered 7-day predictions for any city.
          </p>

          {/* SEARCH */}

          <div className="search-row">

            <div className="search-input-wrapper">

              <span className="search-icon">
                🔍
              </span>

              <input
                className="search-input"
                type="text"
                value={city}
                onChange={(event) =>
                  setCity(event.target.value)
                }
                onKeyDown={handleKeyDown}
                placeholder="Enter city name..."
              />

              {city && (
                <button
                  className="clear-search"
                  onClick={() => setCity('')}
                >
                  ×
                </button>
              )}

            </div>

            <button
              className="search-button"
              onClick={getForecast}
              disabled={loading}
            >
              {loading ? (
                <span className="button-spinner"></span>
              ) : (
                'Search'
              )}
            </button>

          </div>

          <div className="search-helper">
            Press Enter to search
          </div>

          {/* QUICK CITIES */}

          <div className="quick-cities">

            {[
              'Chennai',
              'Bangalore',
              'Mumbai',
              'Delhi',
              'Kochi'
            ].map((name) => (
              <button
                className="quick-city"
                key={name}
                onClick={() => searchCity(name)}
              >
                {name}
              </button>
            ))}

          </div>

          {error && (
            <div className="error-text">
              ⚠️ {error}
            </div>
          )}

        </section>

        {/* =================================================
            WELCOME
        ================================================= */}

        {!forecast && !loading && !error && (
          <section className="welcome-section">

            <div className="welcome-card">

              <div className="welcome-icon">
                🌤️
              </div>

              <h2>
                Check the Weather
              </h2>

              <p>
                Search for a city above to see
                real-time weather conditions and
                your AI-powered 7-day forecast.
              </p>

              <div className="welcome-features">

                <div className="welcome-feature">
                  🌡️ Temperature
                </div>

                <div className="welcome-feature">
                  💧 Humidity
                </div>

                <div className="welcome-feature">
                  🌧️ Rain Probability
                </div>

                <div className="welcome-feature">
                  💨 Wind Speed
                </div>

              </div>

            </div>

          </section>
        )}

        {/* =================================================
            LOADING
        ================================================= */}

        {loading && (
          <section className="welcome-section">

            <div className="welcome-card">

              <div className="welcome-icon">
                🌤️
              </div>

              <h2>
                Getting weather data...
              </h2>

              <p>
                Fetching real-time conditions and
                generating your AI forecast.
              </p>

            </div>

          </section>
        )}

        {/* =================================================
            WEATHER RESULTS
        ================================================= */}

        {forecast && !loading && (

          <main className="weather-results">

            {/* =================================================
                CURRENT WEATHER
            ================================================= */}

            <section className="current-weather-card">

              <div className="current-weather-main">

                <div className="location-info">

                  <h2 className="location-name">
                    {forecast.city || city}
                  </h2>

                  {forecast.country && (
                    <p className="location-country">
                      {forecast.country}
                    </p>
                  )}

                  {forecast.timezone && (
                    <p className="local-time">
                      🕐 {forecast.timezone}
                    </p>
                  )}

                </div>

                <div className="temperature-area">

                  <div className="big-weather-icon">
                    {currentIcon}
                  </div>

                  <div>

                    <div className="temperature">
                      {currentTemperature}
                      <span className="temperature-unit">
                        °C
                      </span>
                    </div>

                    <div className="condition-name">
                      {currentConditionLabel}
                    </div>

                  </div>

                </div>

              </div>

              {/* CURRENT STATS */}

              <div className="weather-stats">

                <div className="weather-stat">

                  <span className="stat-icon">
                    💧
                  </span>

                  <span className="stat-label">
                    Humidity
                  </span>

                  <span className="stat-value">
                    {currentHumidity}%
                  </span>

                </div>

                <div className="weather-stat">

                  <span className="stat-icon">
                    💨
                  </span>

                  <span className="stat-label">
                    Wind
                  </span>

                  <span className="stat-value">
                    {currentWind} km/h
                  </span>

                </div>

                <div className="weather-stat">

                  <span className="stat-icon">
                    🌧️
                  </span>

                  <span className="stat-label">
                    Rain
                  </span>

                  <span className="stat-value">
                    {currentRain} mm
                  </span>

                </div>

                <div className="weather-stat">

                  <span className="stat-icon">
                    ☔
                  </span>

                  <span className="stat-label">
                    Precipitation
                  </span>

                  <span className="stat-value">
                    {currentPrecipitation} mm
                  </span>

                </div>

              </div>

            </section>

            {/* =================================================
                WEATHER TIP
            ================================================= */}

            {weatherTip && (
              <section className="weather-tip-card">

                <div className="tip-icon">
                  💡
                </div>

                <div className="tip-content">

                  <p className="tip-label">
                    Today's insight
                  </p>

                  <h3>
                    Weather Tip
                  </h3>

                  <p>
                    {weatherTip}
                  </p>

                </div>

                <div className="tip-decoration"></div>

              </section>
            )}

            {/* =================================================
                ALERT PREVIEW
            ================================================= */}

            {alerts.length > 0 && (
              <section className="alert-preview-section">

                <div className="section-heading">

                  <div>

                    <p className="section-eyebrow">
                      IMPORTANT
                    </p>

                    <h2>
                      Weather Alerts
                    </h2>

                  </div>

                  <button
                    className="view-alerts-button"
                    onClick={() => setShowAlerts(true)}
                  >
                    View all →
                  </button>

                </div>

                <div className="alert-preview-grid">

                  {alerts.slice(0, 3).map(
                    (alert, index) => {

                      const alertText =
                        typeof alert === 'string'
                          ? alert
                          : alert?.message ||
                            alert?.title ||
                            String(alert)

                      return (
                        <div
                          className="alert-mini-card severity-medium"
                          key={index}
                        >

                          <div className="alert-mini-icon">
                            ⚠️
                          </div>

                          <h3>
                            Weather Alert
                          </h3>

                          <p>
                            {alertText}
                          </p>

                        </div>
                      )
                    }
                  )}

                </div>

              </section>
            )}

            {/* =================================================
                7 DAY FORECAST
            ================================================= */}

            <section className="forecast-section">

              <div className="section-heading">

                <div>

                  <p className="section-eyebrow">
                    PREDICTION
                  </p>

                  <h2>
                    7-Day Forecast
                  </h2>

                </div>

                <p className="forecast-footer">
                  AI predicted conditions
                </p>

              </div>

              <div className="forecast-grid">

                {forecastDays.map(
                  (day, index) => {

                    const rainProbability =
                      getRainProbability(
                        day.rain_probability
                      )

                    let condition

                    if (
                      day.weather_code !== undefined &&
                      day.weather_code !== null
                    ) {
                      condition = getCondition(day)
                    } else if (rainProbability >= 70) {
                      condition = 'rainy'
                    } else if (rainProbability >= 40) {
                      condition = 'drizzle'
                    } else {
                      condition = 'cloudy'
                    }

                    const icon =
                      getWeatherIcon(condition)

                    const label =
                      getConditionLabel(condition)

                    const temperature =
                      day.temperature !== undefined &&
                      day.temperature !== null
                        ? Number(day.temperature).toFixed(1)
                        : '--'

                    const humidity =
                      day.humidity !== undefined &&
                      day.humidity !== null
                        ? Math.round(Number(day.humidity))
                        : '--'

                    const wind =
                      day.windspeed !== undefined &&
                      day.windspeed !== null
                        ? Number(day.windspeed).toFixed(1)
                        : '--'

                    return (

                      <div
                        className={`forecast-day ${
                          index === 0
                            ? 'forecast-today'
                            : ''
                        }`}
                        key={index}
                      >

                        {index === 1 && (
                          <div className="tomorrow-badge">
                            Tomorrow
                          </div>
                        )}

                        <div className="forecast-day-name">
                          {index === 0
                            ? 'Today'
                            : formatDate(day.date)}
                        </div>

                        <div className="forecast-date">
                          {day.date || ''}
                        </div>

                        <div className="forecast-icon">
                          {icon}
                        </div>

                        <div className="forecast-temp">
                          {temperature}°
                        </div>

                        <div className="forecast-condition">
                          {label}
                        </div>

                        <div className="forecast-details">

                          <div className="forecast-badge">
                            🌧️ {rainProbability}%
                          </div>

                          <div className="forecast-badge">
                            💧 {humidity}%
                          </div>

                          <div className="forecast-badge">
                            💨 {wind}
                          </div>

                        </div>

                      </div>
                    )
                  }
                )}

              </div>

              <div className="forecast-footer">
                Rain probability • Humidity • Wind speed
              </div>

            </section>

            {/* =================================================
                DATA SOURCE
            ================================================= */}

            <section className="data-source">

              <p>
                🌐 Current weather: Open-Meteo real-time weather data
              </p>

              <p>
                🤖 Forecast: Machine Learning prediction model
              </p>

            </section>

          </main>
        )}

        {/* =================================================
            FOOTER
        ================================================= */}

        <footer className="app-footer">

          Weather Forecast •
          <strong> AI-powered prediction</strong>

        </footer>

      </div>

      {/* =================================================
          ALERT SIDEBAR
      ================================================= */}

      {showAlerts && (
        <>

          <div
            className="alert-overlay"
            onClick={() => setShowAlerts(false)}
          ></div>

          <aside className="alerts-sidebar alerts-sidebar-open">

            <div className="alerts-sidebar-header">

              <div>

                <p className="sidebar-eyebrow">
                  WEATHER SAFETY
                </p>

                <h2>
                  Alerts
                </h2>

              </div>

              <button
                className="close-alerts"
                onClick={() => setShowAlerts(false)}
              >
                ×
              </button>

            </div>

            {alerts.length === 0 ? (

              <div className="alerts-empty">

                <div className="alerts-empty-icon">
                  ✅
                </div>

                <h3>
                  No active alerts
                </h3>

                <p>
                  No verified weather alerts are
                  currently available for this location.
                </p>

              </div>

            ) : (

              <>

                <div className="alerts-location">
                  📍 {forecast?.city || city}
                </div>

                <div className="alerts-list">

                  {alerts.map((alert, index) => {

                    const alertText =
                      typeof alert === 'string'
                        ? alert
                        : alert?.message ||
                          alert?.title ||
                          String(alert)

                    return (

                      <div
                        className="full-alert-card"
                        key={index}
                      >

                        <div className="full-alert-top">

                          <div className="full-alert-icon">
                            ⚠️
                          </div>

                          <div className="full-alert-title">

                            <h3>
                              Weather Alert
                            </h3>

                            <span className="severity-label severity-label-medium">
                              Advisory
                            </span>

                          </div>

                        </div>

                        <p className="alert-message">
                          {alertText}
                        </p>

                      </div>

                    )
                  })}

                </div>

              </>
            )}

            <div className="alert-disclaimer">
              Weather alerts are shown only when supplied
              by the backend. Normal rain probability is
              not treated as a flood or landslide warning.
            </div>

          </aside>

        </>
      )}

    </div>
  )
}

export default App
