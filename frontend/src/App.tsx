import { useEffect, useState } from 'react'
import './App.css'

interface Summary {
  total_tests: number
  passed: number
  failed: number
  success_rate: number
  failure_breakdown: Record<string, number>
}

interface TestRun {
  test_id: string
  robot_id: string
  timestamp: string
  task_type: string
  battery_level: number
  motor_temperature: number
  cpu_temperature: number
  walking_speed: number
  joint_velocity: number
  torso_angle: number
  grip_force: number
  object_weight: number
  task_duration: number
  collision_detected: boolean
  emergency_stop: boolean
  result: string
  failure_type: string | null
}

interface Hypothesis {
  feature: string
  title: string
  confidence: string
  percent_change: number
  normal_mean: number
  failure_mean: number
  explanation: string
}

interface SafetyEscalation {
  level: string
  events: {
    event: string
    severity: string
  }[]
  message: string
}

interface RootCauseAnalysis {
  hypotheses: Hypothesis[]
  safety_escalation: SafetyEscalation | null
  investigation_confidence: string
  disclaimer: string
}

interface TelemetryAnomaly {
  feature: string
  value: number
  z_score: number
}

interface SafetyEvent {
  event: string
  severity: string
}

interface HistoricalSignal {
  feature: string
  normal_mean: number
  failure_mean: number
  percent_change: number
}


interface InvestigationReport {
  test_id: string
  robot_id: string
  task_type: string
  result: string
  failure_type: string | null
  telemetry_anomalies: TelemetryAnomaly[]
  safety_events: SafetyEvent[]
  historical_signals: HistoricalSignal[]
  root_cause_analysis: RootCauseAnalysis
}



function App() {
  const [summary, setSummary] = useState<Summary | null>(null)
  const [tests, setTests] = useState<TestRun[]>([])
  const [selectedTest, setSelectedTest] = useState<TestRun | null>(null)
  const [investigation, setInvestigation] =
    useState<InvestigationReport | null>(null)
  const [investigationLoading, setInvestigationLoading] =
    useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/summary')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to fetch summary')
        }

        return response.json()
      })
      .then((data: Summary) => {
        setSummary(data)
      })
      .catch((error) => {
        setError(error.message)
      })
  }, [])

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/tests?limit=10')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to fetch test runs')
        }

        return response.json()
      })
      .then((data: TestRun[]) => {
        setTests(data)
      })
      .catch((error) => {
        setError(error.message)
      })
  }, [])

  const investigateTest = async (testId: string) => {
    setError(null)
    setInvestigation(null)
    setInvestigationLoading(true)

    try {
      const testResponse = await fetch(
        `http://127.0.0.1:8000/api/tests/${testId}`,
      )

      if (!testResponse.ok) {
        throw new Error('Failed to fetch test details')
      }

      const testData: TestRun = await testResponse.json()

      setSelectedTest(testData)

      const investigationResponse = await fetch(
        `http://127.0.0.1:8000/api/investigate/${testId}`,
      )

      if (!investigationResponse.ok) {
        throw new Error('Failed to generate investigation')
      }

      const investigationData: InvestigationReport =
        await investigationResponse.json()

      setInvestigation(investigationData)
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message)
      } else {
        setError('Unknown investigation error')
      }
    } finally {
      setInvestigationLoading(false)
    }
  }

  const closeInvestigation = () => {
    setSelectedTest(null)
    setInvestigation(null)
    setInvestigationLoading(false)
  }

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <p className="eyebrow">ROBOTICS VALIDATION PLATFORM</p>

          <h1>Robot Test Intelligence</h1>

          <p className="subtitle">
            Fleet validation & failure intelligence
          </p>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          SYSTEM LIVE
        </div>
      </header>

      <main className="dashboard">
        {error && (
          <div className="error-message">
            Backend error: {error}
          </div>
        )}

        <section>
          <div className="section-heading">
            <div>
              <p className="section-label">FLEET</p>
              <h2>Fleet Overview</h2>
            </div>

            <span className="data-source">LIVE TELEMETRY</span>
          </div>

          <div className="metrics-grid">
            <div className="metric-card">
              <p className="metric-label">TOTAL TESTS</p>
              <h3>{summary?.total_tests.toLocaleString() ?? '—'}</h3>
              <p className="metric-description">
                Validation runs
              </p>
            </div>

            <div className="metric-card">
              <p className="metric-label">PASSED</p>
              <h3>{summary?.passed.toLocaleString() ?? '—'}</h3>
              <p className="metric-description">
                Successful runs
              </p>
            </div>

            <div className="metric-card">
              <p className="metric-label">FAILED</p>
              <h3>{summary?.failed.toLocaleString() ?? '—'}</h3>
              <p className="metric-description">
                Requires investigation
              </p>
            </div>

            <div className="metric-card">
              <p className="metric-label">SUCCESS RATE</p>
              <h3>
                {summary ? `${summary.success_rate}%` : '—'}
              </h3>
              <p className="metric-description">
                Fleet reliability
              </p>
            </div>
          </div>
        </section>

        <div className="analytics-grid">
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="section-label">FAILURES</p>
                <h2>Failure Distribution</h2>
              </div>

              <span className="failure-count">
                {summary?.failed ?? '—'} TOTAL
              </span>
            </div>

            <div className="failure-list">
              {summary &&
                Object.entries(summary.failure_breakdown).map(
                  ([failureType, count]) => {
                    const percentage =
                      summary.failed > 0
                        ? (count / summary.failed) * 100
                        : 0

                    return (
                      <div
                        className="failure-item"
                        key={failureType}
                      >
                        <div className="failure-info">
                          <span>
                            {failureType.replaceAll('_', ' ')}
                          </span>

                          <strong>{count}</strong>
                        </div>

                        <div className="failure-track">
                          <div
                            className="failure-bar"
                            style={{
                              width: `${percentage}%`,
                            }}
                          ></div>
                        </div>
                      </div>
                    )
                  },
                )}
            </div>
          </section>

          <section className="panel test-panel">
            <div className="panel-heading">
              <div>
                <p className="section-label">TEST ACTIVITY</p>
                <h2>Recent Test Runs</h2>
              </div>

              <span className="record-count">
                LATEST 10
              </span>
            </div>

            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>TEST ID</th>
                    <th>ROBOT</th>
                    <th>TASK</th>
                    <th>RESULT</th>
                  </tr>
                </thead>

                <tbody>
                  {tests.map((test) => (
                    <tr
                      key={test.test_id}
                      onClick={() => investigateTest(test.test_id)}
                      className="clickable-row"
                    >
                      <td className="test-id">
                        {test.test_id}
                      </td>

                      <td>{test.robot_id}</td>

                      <td>
                        {test.task_type.replaceAll('_', ' ')}
                      </td>

                      <td>
                        <span
                          className={
                            test.result === 'PASSED'
                              ? 'result passed'
                              : 'result failed'
                          }
                        >
                          <span className="result-dot"></span>
                          {test.result}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>

        {selectedTest && (
          <section className="investigation-panel">
            <div className="investigation-header">
              <div>
                <p className="section-label">
                  TEST INVESTIGATION
                </p>

                <h2>{selectedTest.test_id}</h2>

                <p className="investigation-subtitle">
                  {selectedTest.robot_id} ·{' '}
                  {selectedTest.task_type.replaceAll('_', ' ')}
                </p>
              </div>

              <div className="investigation-actions">
                <span
                  className={
                    selectedTest.result === 'PASSED'
                      ? 'result passed'
                      : 'result failed'
                  }
                >
                  <span className="result-dot"></span>
                  {selectedTest.result}
                </span>

                <button
                  className="close-button"
                  onClick={closeInvestigation}
                >
                  CLOSE
                </button>
              </div>
            </div>

            {selectedTest.failure_type && (
              <div className="failure-alert">
                <span>FAILURE TYPE</span>

                <strong>
                  {selectedTest.failure_type.replaceAll('_', ' ')}
                </strong>
              </div>
            )}

            <div className="telemetry-grid">
              <div className="telemetry-card">
                <span>BATTERY LEVEL</span>
                <strong>{selectedTest.battery_level}%</strong>
              </div>

              <div className="telemetry-card">
                <span>MOTOR TEMP</span>
                <strong>
                  {selectedTest.motor_temperature} °C
                </strong>
              </div>

              <div className="telemetry-card">
                <span>CPU TEMP</span>
                <strong>
                  {selectedTest.cpu_temperature} °C
                </strong>
              </div>

              <div className="telemetry-card">
                <span>WALKING SPEED</span>
                <strong>
                  {selectedTest.walking_speed} m/s
                </strong>
              </div>

              <div className="telemetry-card">
                <span>JOINT VELOCITY</span>
                <strong>{selectedTest.joint_velocity}</strong>
              </div>

              <div className="telemetry-card">
                <span>TORSO ANGLE</span>
                <strong>{selectedTest.torso_angle}°</strong>
              </div>

              <div className="telemetry-card">
                <span>GRIP FORCE</span>
                <strong>{selectedTest.grip_force}</strong>
              </div>

              <div className="telemetry-card">
                <span>OBJECT WEIGHT</span>
                <strong>
                  {selectedTest.object_weight} kg
                </strong>
              </div>

              <div className="telemetry-card">
                <span>TASK DURATION</span>
                <strong>
                  {selectedTest.task_duration} sec
                </strong>
              </div>

              <div className="telemetry-card">
                <span>COLLISION</span>
                <strong>
                  {selectedTest.collision_detected
                    ? 'DETECTED'
                    : 'NONE'}
                </strong>
              </div>

              <div className="telemetry-card">
                <span>EMERGENCY STOP</span>
                <strong>
                  {selectedTest.emergency_stop
                    ? 'TRIGGERED'
                    : 'NO'}
                </strong>
              </div>

              <div className="telemetry-card">
                <span>TIMESTAMP</span>
                <strong className="timestamp-value">
                  {new Date(
                    selectedTest.timestamp,
                  ).toLocaleString()}
                </strong>
              </div>
            </div>

            <div className="intelligence-section">
              <div className="intelligence-heading">
                <div>
                  <p className="section-label">
                    FAILURE INTELLIGENCE
                  </p>
                  <h2>Investigation Intelligence</h2>
                </div>

                <span className="intelligence-badge">
                  ANALYSIS ENGINE
                </span>
              </div>

              {investigationLoading && (
                <div className="intelligence-message">
                  Analyzing telemetry and historical failure
                  patterns...
                </div>
              )}

              {!investigationLoading && investigation && (
                <div className="intelligence-grid">
                  <div className="intelligence-card">
                    <p className="intelligence-card-label">
                      ANOMALY DETECTION
                    </p>

                    {investigation.telemetry_anomalies.length ===
                    0 ? (
                      <p className="intelligence-normal">
                        No ≥2σ telemetry anomalies detected.
                      </p>
                    ) : (
                      <div className="intelligence-list">
                        {investigation.telemetry_anomalies.map(
                          (anomaly) => (
                            <div
                              className="intelligence-row"
                              key={anomaly.feature}
                            >
                              <span>
                                {anomaly.feature
                                  .replaceAll('_', ' ')
                                  .toUpperCase()}
                              </span>

                              <strong>
                                Z {anomaly.z_score}
                              </strong>
                            </div>
                          ),
                        )}
                      </div>
                    )}
                  </div>

                  <div className="intelligence-card">
                    <p className="intelligence-card-label">
                      SAFETY EVENTS
                    </p>

                    {investigation.safety_events.length === 0 ? (
                      <p className="intelligence-normal">
                        No safety events detected.
                      </p>
                    ) : (
                      <div className="intelligence-list">
                        {investigation.safety_events.map(
                          (event) => (
                            <div
                              className="intelligence-row safety"
                              key={event.event}
                            >
                              <span>
                                {event.event.replaceAll('_', ' ')}
                              </span>

                              <strong>
                                {event.severity}
                              </strong>
                            </div>
                          ),
                        )}
                      </div>
                    )}
                  </div>

                  <div className="intelligence-card historical-card">
                    <p className="intelligence-card-label">
                      HISTORICAL FAILURE SIGNALS
                    </p>

                    {investigation.historical_signals.length ===
                    0 ? (
                      <p className="intelligence-normal">
                        No strong historical signals detected.
                      </p>
                    ) : (
                      <div className="signal-list">
                        {investigation.historical_signals.map(
                          (signal) => (
                            <div
                              className="signal-row"
                              key={signal.feature}
                            >
                              <div>
                                <strong>
                                  {signal.feature
                                    .replaceAll('_', ' ')
                                    .toUpperCase()}
                                </strong>

                                <p>
                                  Normal {signal.normal_mean} ·
                                  Failure {signal.failure_mean}
                                </p>
                              </div>

                              <span
                                className={
                                  signal.percent_change >= 0
                                    ? 'signal-change positive'
                                    : 'signal-change negative'
                                }
                              >
                                {signal.percent_change > 0
                                  ? '+'
                                  : ''}
                                {signal.percent_change}%
                              </span>
                            </div>
                          ),
                        )}
                      </div>
                    )}

                    <p className="signal-note">
                      Historical signals compare this failure
                      category with successful runs of the same
                      task. They indicate association, not
                      causation.
                    </p>
                  </div>
                  {investigation.root_cause_analysis && (
                    <div className="root-cause-section">

                      <div className="root-cause-header">
                        <div>
                          <p className="intelligence-card-label">
                            ROOT CAUSE HYPOTHESES
                          </p>

                          <h2>Likely Contributing Factors</h2>
                        </div>

                        <div
                          className={`confidence-badge ${investigation.root_cause_analysis.investigation_confidence.toLowerCase()}`}
                        >
                          {investigation.root_cause_analysis.investigation_confidence}
                          <span> CONFIDENCE</span>
                        </div>
                      </div>

                      <div className="hypothesis-list">

                        {investigation.root_cause_analysis.hypotheses.map(
                          (hypothesis, index) => (

                            <div
                              className="hypothesis-card"
                              key={hypothesis.feature}
                            >

                              <div className="hypothesis-number">
                                {String(index + 1).padStart(2, '0')}
                              </div>

                              <div className="hypothesis-content">

                                <div className="hypothesis-title-row">

                                  <h3>
                                    {hypothesis.title}
                                  </h3>

                                  <span
                                    className={`hypothesis-confidence ${hypothesis.confidence.toLowerCase()}`}
                                  >
                                    {hypothesis.confidence}
                                  </span>

                                </div>

                                <p>
                                  {hypothesis.explanation}
                                </p>

                                <div className="hypothesis-metrics">

                                  <span>
                                    NORMAL
                                    <strong>
                                      {hypothesis.normal_mean}
                                    </strong>
                                  </span>

                                  <span>
                                    FAILURE
                                    <strong>
                                      {hypothesis.failure_mean}
                                    </strong>
                                  </span>

                                  <span>
                                    CHANGE
                                    <strong>
                                      {hypothesis.percent_change > 0 ? '+' : ''}
                                      {hypothesis.percent_change}%
                                    </strong>
                                  </span>

                                </div>

                              </div>

                            </div>
                          )
                        )}

                      </div>

                      {investigation.root_cause_analysis.safety_escalation && (
                        <div className="safety-escalation">

                          <div>
                            <p>SAFETY ESCALATION</p>

                            <strong>
                              {
                                investigation.root_cause_analysis
                                  .safety_escalation.message
                              }
                            </strong>
                          </div>

                          <span>
                            {
                              investigation.root_cause_analysis
                                .safety_escalation.level
                            }
                          </span>

                        </div>
                      )}

                      <p className="root-cause-disclaimer">
                        {investigation.root_cause_analysis.disclaimer}
                      </p>

                    </div>
                  )}
                </div>
              )}
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

export default App