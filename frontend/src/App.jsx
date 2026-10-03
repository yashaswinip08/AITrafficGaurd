import { useMemo, useState } from 'react'
import './App.css'

const incidents = [
  {
    id: 1,
    type: 'red_light',
    title: 'Signal breach',
    camera: 'cam_01',
    track: 101,
    plate: 'KA05AB2045',
    confidence: 94,
    timestamp: '08:12:45',
    frame: 148,
    severity: 'High',
    location: 'Main Cross Road',
    image:
      'https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=80',
  },
  {
    id: 2,
    type: 'no_helmet',
    title: 'Helmet violation',
    camera: 'cam_02',
    track: 202,
    plate: 'MH12XY8855',
    confidence: 87,
    timestamp: '08:45:12',
    frame: 422,
    severity: 'Medium',
    location: 'Industrial Loop',
    image:
      'https://images.unsplash.com/photo-1517849845537-4d257902454a?auto=format&fit=crop&w=1200&q=80',
  },
  {
    id: 3,
    type: 'red_light',
    title: 'Signal breach',
    camera: 'cam_03',
    track: 305,
    plate: 'TN74AA6721',
    confidence: 90,
    timestamp: '09:02:03',
    frame: 530,
    severity: 'High',
    location: 'Airport Junction',
    image:
      'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=1200&q=80',
  },
  {
    id: 4,
    type: 'no_helmet',
    title: 'Helmet violation',
    camera: 'cam_01',
    track: 412,
    plate: 'DL08QQ7614',
    confidence: 89,
    timestamp: '09:18:56',
    frame: 688,
    severity: 'Medium',
    location: 'North Avenue',
    image:
      'https://images.unsplash.com/photo-1544636331-e26879cd4d9b?auto=format&fit=crop&w=1200&q=80',
  },
]

const typeMeta = {
  red_light: { label: 'Red light', accent: 'danger' },
  no_helmet: { label: 'No helmet', accent: 'warning' },
  all: { label: 'All', accent: 'neutral' },
}

function App() {
  const [selectedType, setSelectedType] = useState('all')
  const [selectedCamera, setSelectedCamera] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [liveMode, setLiveMode] = useState(true)
  const [selectedFile, setSelectedFile] = useState(null)
  const [scanResult, setScanResult] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [scanMessage, setScanMessage] = useState('')
  const [plateHint, setPlateHint] = useState('')

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setScanMessage('Upload a vehicle image first to run the AI scan.')
      setScanResult(null)
      return
    }

    setIsAnalyzing(true)
    setScanMessage('')

    const formData = new FormData()
    formData.append('file', selectedFile)
    formData.append('violation_type', selectedType === 'all' ? 'red_light' : selectedType)
    if (plateHint.trim()) {
      formData.append('plate_hint', plateHint.trim())
    }

    try {
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Scan failed')
      }

      const payload = await response.json()
      setScanResult(payload)
      setScanMessage(payload.status === 'ready' ? 'AI scan complete.' : 'OCR needs a clearer image for a confident read.')
    } catch (error) {
      const fallback = {
        status: 'review_needed',
        violation_type: selectedType === 'all' ? 'red_light' : selectedType,
        plate: 'UNKNOWN',
        confidence: 82,
        valid_plate_format: false,
        reason: 'Uploaded image was processed in demo mode while the local OCR service was unavailable.',
        recommendation: 'Please retry with a clearer front or rear plate image for stronger OCR confidence.',
      }
      setScanResult(fallback)
      setScanMessage('Demo fallback mode: the image was queued for analysis, but the OCR service is offline.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const cameraOptions = ['all', ...new Set(incidents.map((item) => item.camera))]

  const filteredIncidents = useMemo(() => {
    return incidents.filter((item) => {
      const typeMatch = selectedType === 'all' || item.type === selectedType
      const cameraMatch = selectedCamera === 'all' || item.camera === selectedCamera
      const search = searchTerm.trim().toLowerCase()
      const searchMatch =
        !search ||
        `${item.plate} ${item.location} ${item.camera}`.toLowerCase().includes(search)

      return typeMatch && cameraMatch && searchMatch
    })
  }, [selectedType, selectedCamera, searchTerm])

  const stats = useMemo(() => {
    const redLight = filteredIncidents.filter((item) => item.type === 'red_light').length
    const noHelmet = filteredIncidents.filter((item) => item.type === 'no_helmet').length
    const avgConfidence =
      filteredIncidents.length > 0
        ? Math.round(
            filteredIncidents.reduce((sum, item) => sum + item.confidence, 0) /
              filteredIncidents.length,
          )
        : 0

    return { total: filteredIncidents.length, redLight, noHelmet, avgConfidence }
  }, [filteredIncidents])

  const previewImage = selectedFile ? URL.createObjectURL(selectedFile) : filteredIncidents[0]?.image ?? incidents[0].image

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-badge">🚦</div>
          <div>
            <p className="eyebrow">Monitoring</p>
            <h2>AI Traffic Guard</h2>
          </div>
        </div>

        <div className="panel-block">
          <label className="field-label">Violation type</label>
          <div className="chip-group">
            {Object.entries(typeMeta).map(([value, meta]) => (
              <button
                key={value}
                type="button"
                className={`chip ${selectedType === value ? 'active' : ''}`}
                onClick={() => setSelectedType(value)}
              >
                {meta.label}
              </button>
            ))}
          </div>
        </div>

        <div className="panel-block">
          <label className="field-label" htmlFor="cameraFilter">
            Camera
          </label>
          <select
            id="cameraFilter"
            value={selectedCamera}
            onChange={(event) => setSelectedCamera(event.target.value)}
            className="select-box"
          >
            {cameraOptions.map((camera) => (
              <option key={camera} value={camera}>
                {camera === 'all' ? 'All cameras' : camera}
              </option>
            ))}
          </select>
        </div>

        <div className="panel-block">
          <label className="field-label" htmlFor="searchInput">
            Search
          </label>
          <input
            id="searchInput"
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
            placeholder="Plate, camera, location"
            className="search-input"
          />
        </div>

        <div className="panel-block toggle-row">
          <span>Live monitoring</span>
          <button
            type="button"
            className={`toggle ${liveMode ? 'on' : ''}`}
            onClick={() => setLiveMode((value) => !value)}
            aria-pressed={liveMode}
          >
            <span className="toggle-knob" />
          </button>
        </div>

        <div className="panel-block system-box">
          <p className="muted-label">System health</p>
          <div className="status-line">
            <span className="dot green" />
            Deployment online
          </div>
          <div className="status-line">
            <span className="dot amber" />
            Evidence sync ready
          </div>
          <div className="status-line">
            <span className="dot blue" />
            CPU fallback active
          </div>
        </div>

        <div className="panel-block scan-box">
          <label className="field-label" htmlFor="vehicleUpload">
            Vehicle scan
          </label>

          <input
            id="vehicleUpload"
            type="file"
            accept="image/*"
            className="file-picker"
            onChange={(event) => {
              const file = event.target.files?.[0] ?? null
              setSelectedFile(file)
              setScanResult(null)
              setScanMessage(file ? 'Image ready for AI analysis.' : '')
            }}
          />

          <label className="field-label optional-label" htmlFor="plateHint">
            Plate hint (optional)
          </label>
          <input
            id="plateHint"
            value={plateHint}
            onChange={(event) => setPlateHint(event.target.value)}
            placeholder="e.g. KA01AB1234"
            className="search-input"
          />

          <button type="button" className="action-button primary full-width" onClick={handleAnalyze} disabled={isAnalyzing}>
            {isAnalyzing ? 'Analyzing...' : 'Scan vehicle'}
          </button>

          {scanMessage && <p className="scan-message">{scanMessage}</p>}

          {scanResult && (
            <div className="analysis-card">
              <div className="analysis-header">
                <span className="tag tag-muted">{scanResult.violation_type === 'no_helmet' ? 'No helmet' : 'Red light'}</span>
                <span className="confidence-badge">{scanResult.confidence}% OCR confidence</span>
              </div>

              <div className="analysis-grid">
                <div>
                  <small>Detected plate</small>
                  <strong>{scanResult.plate ?? 'UNKNOWN'}</strong>
                </div>
                <div>
                  <small>Result</small>
                  <strong>{scanResult.status === 'ready' ? 'Violation flagged' : 'Needs review'}</strong>
                </div>
              </div>

              <p>{scanResult.reason}</p>
              <p className="recommendation">{scanResult.recommendation}</p>
            </div>
          )}
        </div>
      </aside>

      <main className="content-area">
        <header className="topbar">
          <div>
            <p className="eyebrow">Operations desk</p>
            <h1>Traffic enforcement overview</h1>
          </div>
          <div className="topbar-actions">
            <button type="button" className="action-button ghost">
              Export CSV
            </button>
            <button type="button" className="action-button primary" onClick={handleAnalyze}>
              Run demo scan
            </button>
          </div>
        </header>

        <section className="stats-grid">
          <article className="stat-card">
            <span>Total violations</span>
            <strong>{stats.total}</strong>
            <small>Across all cameras</small>
          </article>
          <article className="stat-card danger">
            <span>Red light</span>
            <strong>{stats.redLight}</strong>
            <small>Critical signal breaches</small>
          </article>
          <article className="stat-card warning">
            <span>No helmet</span>
            <strong>{stats.noHelmet}</strong>
            <small>Safety violations</small>
          </article>
          <article className="stat-card primary">
            <span>Avg confidence</span>
            <strong>{stats.avgConfidence}%</strong>
            <small>Recognition accuracy</small>
          </article>
        </section>

        <section className="dashboard-grid">
          <div className="panel large-panel">
            <div className="panel-header">
              <h3>Evidence stream</h3>
              <span className="panel-pill">{liveMode ? 'Live' : 'Review'}</span>
            </div>

            <div className="hero-traffic">
              <img
                src={previewImage}
                alt="Traffic violation evidence"
              />
              <div className="hero-overlay">
                <span className="tag">{typeMeta[filteredIncidents[0]?.type ?? 'red_light'].label}</span>
                <h4>{scanResult?.plate ?? filteredIncidents[0]?.plate ?? 'KA05AB2045'}</h4>
                <p>
                  {scanResult?.status === 'ready' ? 'AI scan complete' : filteredIncidents[0]?.location ?? 'Main Cross Road'} •{' '}
                  {selectedFile?.name ?? filteredIncidents[0]?.camera ?? 'cam_01'}
                </p>
              </div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <h3>Latest alerts</h3>
              <span className="panel-pill neutral">{filteredIncidents.length} active</span>
            </div>
            <div className="alert-list">
              {filteredIncidents.slice(0, 4).map((item) => (
                <div key={item.id} className="alert-item">
                  <div className={`alert-dot ${item.type === 'red_light' ? 'danger' : 'warning'}`} />
                  <div>
                    <strong>{item.title}</strong>
                    <p>
                      {item.plate} • {item.location}
                    </p>
                  </div>
                  <span>{item.timestamp}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="panel table-panel">
          <div className="panel-header">
            <h3>Violation records</h3>
            <span className="panel-pill neutral">Updated just now</span>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Camera</th>
                  <th>Track</th>
                  <th>Plate</th>
                  <th>Confidence</th>
                  <th>Location</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {filteredIncidents.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <span className={`type-pill ${item.type === 'red_light' ? 'danger' : 'warning'}`}>
                        {typeMeta[item.type].label}
                      </span>
                    </td>
                    <td>{item.camera}</td>
                    <td>{item.track}</td>
                    <td>{item.plate}</td>
                    <td>{item.confidence}%</td>
                    <td>{item.location}</td>
                    <td>{item.timestamp}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
