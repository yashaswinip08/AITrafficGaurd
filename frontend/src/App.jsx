import { useEffect, useRef, useState } from 'react'
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
  const [activeView, setActiveView] = useState('overview')
  const [scanViolationType, setScanViolationType] = useState('red_light')
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [scanResult, setScanResult] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [scanMessage, setScanMessage] = useState('')
  const [plateHint, setPlateHint] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef(null)
  const cameraInputRef = useRef(null)
  const previewUrlRef = useRef('')

  useEffect(() => {
    return () => {
      if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current)
    }
  }, [])

  const handleFileSelection = (file) => {
    if (!file) return
    if (!file.type.startsWith('image/')) {
      setScanMessage('Choose a JPG, PNG, or other supported image file.')
      return
    }
    if (file.size > 15 * 1024 * 1024) {
      setScanMessage('Image is larger than 15 MB. Choose a smaller file.')
      return
    }

    if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current)
    previewUrlRef.current = URL.createObjectURL(file)
    setPreviewUrl(previewUrlRef.current)
    setSelectedFile(file)
    setScanResult(null)
    setScanMessage('Image ready for vehicle and plate analysis.')
  }

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setScanMessage('Upload a vehicle image first to run the AI scan.')
      setScanResult(null)
      return
    }

    setIsAnalyzing(true)
    setScanMessage('')
    setScanResult(null)

    const formData = new FormData()
    formData.append('file', selectedFile)
    formData.append('violation_type', scanViolationType)
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
      if (payload.status === 'error') {
        throw new Error(payload.message || 'The image could not be analyzed.')
      }
      setScanResult(payload)
      if (payload.wheel_category === 'unavailable') {
        setScanMessage('Plate analysis returned. Vehicle classification is unavailable in the current backend.')
      } else if (payload.status === 'ready') {
        setScanMessage('Image analysis complete. Review the plate and context before enforcement.')
      } else {
        setScanMessage('Analysis complete; the plate needs manual review.')
      }
    } catch {
      setScanMessage('Could not reach the local analysis service. Check that the Python API is running, then retry.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setIsDragging(false)
    handleFileSelection(event.dataTransfer.files?.[0])
  }

  const handleExportCsv = () => {
    const headers = ['Type', 'Camera', 'Track', 'Plate', 'Confidence', 'Location', 'Time']
    const rows = filteredIncidents.map((item) => [
      typeMeta[item.type].label,
      item.camera,
      item.track,
      item.plate,
      `${item.confidence}%`,
      item.location,
      item.timestamp,
    ])
    const csv = [headers, ...rows].map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(',')).join('\n')
    const downloadUrl = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }))
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = 'traffic-guard-records.csv'
    link.click()
    URL.revokeObjectURL(downloadUrl)
  }

  const cameraOptions = ['all', ...new Set(incidents.map((item) => item.camera))]
  const search = searchTerm.trim().toLowerCase()
  const filteredIncidents = incidents.filter((item) => {
    const typeMatch = selectedType === 'all' || item.type === selectedType
    const cameraMatch = selectedCamera === 'all' || item.camera === selectedCamera
    const searchMatch = !search || `${item.plate} ${item.location} ${item.camera}`.toLowerCase().includes(search)
    return typeMatch && cameraMatch && searchMatch
  })
  const redLight = filteredIncidents.filter((item) => item.type === 'red_light').length
  const noHelmet = filteredIncidents.filter((item) => item.type === 'no_helmet').length
  const avgConfidence = filteredIncidents.length
    ? Math.round(filteredIncidents.reduce((sum, item) => sum + item.confidence, 0) / filteredIncidents.length)
    : 0
  const stats = { total: filteredIncidents.length, redLight, noHelmet, avgConfidence }

  const clearSelectedFile = () => {
    if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current)
    previewUrlRef.current = ''
    setPreviewUrl('')
    setSelectedFile(null)
    setScanResult(null)
    setPlateHint('')
    setScanMessage('')
  }

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

      </aside>

      <main className="content-area">
        <header className="topbar">
          <div>
            <p className="eyebrow">Operations desk</p>
            <h1>Traffic enforcement overview</h1>
          </div>
          <div className="topbar-actions">
            <button type="button" className="action-button ghost" onClick={handleExportCsv}>
              Export CSV
            </button>
            <button type="button" className="action-button primary" onClick={() => setActiveView('scan')}>
              New scan
            </button>
          </div>
        </header>

        <nav className="workspace-tabs" aria-label="Dashboard views">
          {[
            ['overview', 'Overview'],
            ['scan', 'Scan & analyze'],
            ['records', 'Violation records'],
          ].map(([view, label]) => (
            <button
              key={view}
              type="button"
              className={`workspace-tab ${activeView === view ? 'active' : ''}`}
              onClick={() => setActiveView(view)}
              aria-current={activeView === view ? 'page' : undefined}
            >
              {label}
            </button>
          ))}
          <span className="workspace-context">{filteredIncidents.length} records in current view</span>
        </nav>

        {activeView === 'overview' && (
          <>
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
                src={filteredIncidents[0]?.image ?? incidents[0].image}
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
          </>
        )}

        {activeView === 'scan' && (
          <section className="scan-workspace">
            <div className="panel scan-evidence-panel">
              <div className="panel-header">
                <div>
                  <p className="eyebrow">Evidence intake</p>
                  <h3>Upload a vehicle image</h3>
                </div>
                <span className="panel-pill neutral">JPG · PNG · WEBP · up to 15 MB</span>
              </div>

              <div
                className={`drop-zone ${isDragging ? 'dragging' : ''} ${previewUrl ? 'has-preview' : ''}`}
                onDragEnter={(event) => { event.preventDefault(); setIsDragging(true) }}
                onDragOver={(event) => event.preventDefault()}
                onDragLeave={(event) => {
                  if (!event.currentTarget.contains(event.relatedTarget)) setIsDragging(false)
                }}
                onDrop={handleDrop}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  className="visually-hidden"
                  onChange={(event) => {
                    handleFileSelection(event.target.files?.[0])
                    event.target.value = ''
                  }}
                />
                <input
                  ref={cameraInputRef}
                  type="file"
                  accept="image/*"
                  capture="environment"
                  className="visually-hidden"
                  onChange={(event) => {
                    handleFileSelection(event.target.files?.[0])
                    event.target.value = ''
                  }}
                />
                {previewUrl ? (
                  <img className="scan-preview" src={previewUrl} alt="Selected vehicle for analysis" />
                ) : (
                  <div className="drop-prompt">
                    <span className="upload-symbol" aria-hidden="true">+</span>
                    <strong>Drop the vehicle photo here</strong>
                    <span>Use a clear front or rear view with the registration plate visible.</span>
                  </div>
                )}
                {selectedFile && <div className="file-caption">{selectedFile.name}</div>}
              </div>

              <div className="upload-actions">
                <button type="button" className="action-button ghost" onClick={() => fileInputRef.current?.click()}>
                  Choose image
                </button>
                <button type="button" className="action-button ghost" onClick={() => cameraInputRef.current?.click()}>
                  Capture photo
                </button>
                {selectedFile && (
                  <button
                    type="button"
                    className="text-button"
                    onClick={clearSelectedFile}
                  >
                    Clear image
                  </button>
                )}
              </div>

              <div className="scan-options">
                <div className="option-field">
                  <span className="field-label">Review category</span>
                  <div className="chip-group">
                    {['red_light', 'no_helmet'].map((type) => (
                      <button
                        key={type}
                        type="button"
                        className={`chip ${scanViolationType === type ? 'active' : ''}`}
                        onClick={() => setScanViolationType(type)}
                      >
                        {typeMeta[type].label}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="option-field">
                  <label className="field-label" htmlFor="plateHint">Plate correction (optional)</label>
                  <input
                    id="plateHint"
                    value={plateHint}
                    onChange={(event) => setPlateHint(event.target.value)}
                    placeholder="Enter if OCR is unclear"
                    className="search-input"
                  />
                </div>
              </div>

              <div className="scan-submit-row">
                <p className="scan-message" role="status">{scanMessage || 'AI will classify the vehicle and read the plate. A reviewer confirms violations.'}</p>
                <button type="button" className="action-button primary scan-submit" onClick={handleAnalyze} disabled={isAnalyzing || !selectedFile}>
                  {isAnalyzing ? 'Analyzing image…' : 'Run AI analysis'}
                </button>
              </div>
            </div>

            <div className="panel scan-result-panel">
              <div className="panel-header">
                <div>
                  <p className="eyebrow">Model output</p>
                  <h3>Analysis report</h3>
                </div>
                <span className={`result-status ${scanResult?.status === 'ready' ? 'ready' : ''}`}>
                  <span className="dot" />
                  {scanResult ? (scanResult.status === 'ready' ? 'Review ready' : 'Needs review') : 'Waiting for image'}
                </span>
              </div>

              {scanResult ? (
                <>
                  <div className="result-plate">
                    <span>Number plate</span>
                    <strong>{scanResult.plate}</strong>
                    <small>OCR confidence · {scanResult.confidence}%</small>
                  </div>
                  <div className="result-metrics">
                    <div><span>Vehicle</span><strong>{scanResult.wheel_category ?? 'unclassified'}</strong></div>
                    <div><span>Model class</span><strong>{scanResult.vehicle_class ?? 'unknown'}</strong></div>
                    <div><span>Detection confidence</span><strong>{scanResult.vehicle_confidence ?? 0}%</strong></div>
                    <div><span>Selected review</span><strong>{typeMeta[scanResult.violation_type]?.label ?? scanResult.violation_type}</strong></div>
                  </div>
                  <div className="ai-summary">
                    <span>AI analysis</span>
                    <p>{scanResult.ai_analysis ?? scanResult.reason}</p>
                  </div>
                  {scanResult.wheel_category === '6+ wheels (estimated)' && (
                    <p className="classification-note">Heavy category is inferred from a bus/truck detection; the model does not count exact wheels.</p>
                  )}
                  {scanResult.wheel_category === 'unavailable' && (
                    <p className="classification-note">Vehicle classifier unavailable. Check the YOLO package and model weights in the local backend.</p>
                  )}
                  {scanResult.wheel_category === 'unclassified' && (
                    <p className="classification-note">No supported vehicle class was detected. Try a clearer image showing the full vehicle.</p>
                  )}
                  <div className="review-note">
                    <span aria-hidden="true">i</span>
                    <p>{scanResult.recommendation}</p>
                  </div>
                </>
              ) : (
                <div className="empty-report">
                  <span className="report-mark" aria-hidden="true">AI</span>
                  <strong>Analysis appears here</strong>
                  <p>Upload a photo to see OCR plate text, vehicle class, model confidence, and review guidance.</p>
                  <div className="pipeline-steps">
                    <span><b>01</b> Vehicle detection</span>
                    <span><b>02</b> Plate OCR</span>
                    <span><b>03</b> Evidence review</span>
                  </div>
                </div>
              )}
            </div>
          </section>
        )}

        {activeView === 'records' && <section className="panel table-panel">
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
        </section>}
      </main>
    </div>
  )
}

export default App
