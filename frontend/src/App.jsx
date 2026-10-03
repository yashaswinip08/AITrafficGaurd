import { useEffect, useRef, useState } from 'react'
import { normalizePlateText } from './plateText.js'
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
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      setScanMessage('Choose a JPG, PNG, or WEBP image.')
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
    setScanMessage('Image ready. OCR will run locally in your browser.')
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

    try {
      setScanMessage('Loading the bundled OCR engine…')
      const { analyzeImage } = await import('./ocr.js')
      const result = await analyzeImage(selectedFile, ({ status, progress }) => {
        const percentage = Number.isFinite(progress) ? ` ${Math.round(progress * 100)}%` : ''
        setScanMessage(`${status}${percentage}`)
      })

      const manualReading = normalizePlateText(plateHint)
      const plateReading = manualReading.validFormat ? manualReading : result.plateReading
      const confidence = manualReading.validFormat
        ? 100
        : Math.round(plateReading?.confidence ?? result.confidence)
      const hasPlate = Boolean(plateReading?.validFormat)
      const validPlate = manualReading.validFormat || (hasPlate && confidence >= 50)
      const plate = hasPlate ? plateReading.cleanedText : 'UNKNOWN'
      const reviewLabel = typeMeta[scanViolationType].label.toLowerCase()
      const analysis = manualReading.validFormat
        ? `Plate ${plate} was entered as a manual correction. The selected category is ${reviewLabel}; this image-only tool does not confirm the violation or classify the vehicle.`
        : validPlate
        ? `OCR read plate ${plate} with ${confidence}% confidence. The selected category is ${reviewLabel}; this image-only tool does not confirm the violation or classify the vehicle.`
        : hasPlate
          ? `OCR suggests plate ${plate}, but confidence is only ${confidence}%. Verify the text or enter a correction. The selected category is ${reviewLabel}; this tool does not confirm violations.`
        : `OCR did not find a confidently formatted registration plate. The selected category is ${reviewLabel}; this image-only tool does not confirm the violation or classify the vehicle.`

      setScanResult({
        status: validPlate ? 'ready' : 'review_needed',
        violation_type: scanViolationType,
        plate,
        confidence,
        confidence_label: manualReading.validFormat ? 'Manual correction' : 'OCR confidence',
        valid_plate_format: validPlate,
        ai_analysis: analysis,
        ocr_text: result.text,
        recommendation: 'Compare this still image with contextual footage before recording an enforcement action.',
      })
      setScanMessage(validPlate ? 'OCR complete. Review the plate before using it.' : 'OCR complete. Manual review is required.')
    } catch (error) {
      console.error('Browser OCR failed:', error)
      setScanMessage('OCR could not start. Reload the app and try again.')
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
          <span>Demo monitoring</span>
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
          <div className="status-line"><span className="dot green" />OCR runs in this browser</div>
          <div className="status-line"><span className="dot amber" />English model bundled</div>
          <div className="status-line"><span className="dot blue" />Images stay on device</div>
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
          <span className="workspace-context">{filteredIncidents.length} demo records in current view</span>
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
            <small>Average sample confidence</small>
          </article>
        </section>

        <section className="dashboard-grid">
          <div className="panel large-panel">
            <div className="panel-header">
              <h3>Evidence stream</h3>
              <span className="panel-pill">{liveMode ? 'Sample' : 'Review'}</span>
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
              <span className="panel-pill neutral">{filteredIncidents.length} demo alerts</span>
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
                  accept="image/jpeg,image/png,image/webp"
                  className="visually-hidden"
                  onChange={(event) => {
                    handleFileSelection(event.target.files?.[0])
                    event.target.value = ''
                  }}
                />
                <input
                  ref={cameraInputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
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
                <p className="scan-message" role="status">{scanMessage || 'Plate OCR runs in your browser. Vehicle class and violation need a separate human review.'}</p>
                <button type="button" className="action-button primary scan-submit" onClick={handleAnalyze} disabled={isAnalyzing || !selectedFile}>
                  {isAnalyzing ? 'Reading image…' : 'Read plate'}
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
                    <small>{scanResult.confidence_label} · {scanResult.confidence}%</small>
                  </div>
                  <div className="result-metrics">
                    <div><span>Vehicle class</span><strong>Not analyzed</strong></div>
                    <div><span>Violation</span><strong>Needs review</strong></div>
                    <div><span>Selected review</span><strong>{typeMeta[scanResult.violation_type]?.label ?? scanResult.violation_type}</strong></div>
                  </div>
                  <div className="ai-summary">
                    <span>AI analysis</span>
                    <p>{scanResult.ai_analysis ?? scanResult.reason}</p>
                  </div>
                  <div className="ai-summary">
                    <span>Recognized text</span>
                    <p>{scanResult.ocr_text || 'No text detected.'}</p>
                  </div>
                  <p className="classification-note">This single-app deployment reads plate text only. It does not classify vehicles or determine violations.</p>
                  <div className="review-note">
                    <span aria-hidden="true">i</span>
                    <p>{scanResult.recommendation}</p>
                  </div>
                </>
              ) : (
                <div className="empty-report">
                  <span className="report-mark" aria-hidden="true">AI</span>
                  <strong>Analysis appears here</strong>
                  <p>Upload a photo to see locally recognized plate text and review guidance. Your image is not sent to a server.</p>
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
