import { useState, useEffect, useRef } from "react";
import {
  ShieldCheck,
  Search,
  AlertTriangle,
  FileText,
  Database,
  CheckCircle2,
  Sparkles,
} from "lucide-react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [question, setQuestion] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const [animatedConfidence, setAnimatedConfidence] = useState(0);
  const [animatedClaims, setAnimatedClaims] = useState(0);
  const [animatedEvidence, setAnimatedEvidence] = useState(0);

  const metricsRef = useRef(null);
  const animationStarted = useRef(false);

  // =========================================================
  // ASK QUESTION
  // =========================================================

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setData(null);

    setAnimatedConfidence(0);
    setAnimatedClaims(0);
    setAnimatedEvidence(0);
    animationStarted.current = false;

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error("Request failed");
      }

      const result = await response.json();

      setData(result);
    } catch (error) {
      console.error("API Error:", error);

      setData({
        error:
          "Could not connect to the Knowledge Integrity Engine.",
      });
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // ENTER KEY
  // =========================================================

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  };

  // =========================================================
  // CLEAN GENERATED ANSWER
  // =========================================================
  //
  // Removes unwanted source/path information accidentally
  // included by the generated answer.
  //
  // Examples removed:
  //
  // 【C:\Users\hp\...\test_policy.txt】
  // [C:\Users\hp\...\test_policy.txt]
  // (Source: C:\Users\hp\...)
  // [Source: C:\Users\hp\...]
  // Source: C:\Users\hp\...
  //
  // =========================================================

  const cleanAnswer = (answer) => {
    if (!answer || typeof answer !== "string") {
      return "";
    }

    let cleaned = answer;

    // Remove 【full/path/to/file】
    cleaned = cleaned.replace(
      /【[^】]*(?:\\|\/)[^】]*】/g,
      ""
    );

    // Remove [full/path/to/file]
    cleaned = cleaned.replace(
      /\[[^\]]*(?:\\|\/)[^\]]*\]/g,
      ""
    );

    // Remove (Source: ...)
    cleaned = cleaned.replace(
      /\(\s*Source\s*:\s*[^)]*\)/gi,
      ""
    );

    // Remove [Source: ...]
    cleaned = cleaned.replace(
      /\[\s*Source\s*:\s*[^\]]*\]/gi,
      ""
    );

    // Remove 【Source: ...】
    cleaned = cleaned.replace(
      /【\s*Source\s*:\s*[^】]*】/gi,
      ""
    );

    // Remove Source: C:\...
    cleaned = cleaned.replace(
      /Source\s*:\s*[A-Za-z]:\\[^\n\r]*/gi,
      ""
    );

    // Remove Source: /home/...
    cleaned = cleaned.replace(
      /Source\s*:\s*\/[^\n\r]*/gi,
      ""
    );

    // Remove numeric source references such as [1]
    cleaned = cleaned.replace(
      /\[\d+\]/g,
      ""
    );

    // Remove excessive spaces.
    cleaned = cleaned.replace(
      /[ \t]{2,}/g,
      " "
    );

    // Remove spaces before punctuation.
    cleaned = cleaned.replace(
      /\s+([,.!?;:])/g,
      "$1"
    );

    // Clean excessive blank lines.
    cleaned = cleaned.replace(
      /\n{3,}/g,
      "\n\n"
    );

    return cleaned.trim();
  };

  // =========================================================
  // CLEAN EVIDENCE TEXT
  // =========================================================

  const cleanEvidenceText = (text) => {
    if (!text || typeof text !== "string") {
      return "No evidence text available.";
    }

    let cleaned = text;

    // Remove 【path】
    cleaned = cleaned.replace(
      /【[^】]*(?:\\|\/)[^】]*】/g,
      ""
    );

    // Remove [path]
    cleaned = cleaned.replace(
      /\[[^\]]*(?:\\|\/)[^\]]*\]/g,
      ""
    );

    // Remove Source: Windows path
    cleaned = cleaned.replace(
      /Source\s*:\s*[A-Za-z]:\\[^\n\r]*/gi,
      ""
    );

    // Remove Source: Linux path
    cleaned = cleaned.replace(
      /Source\s*:\s*\/[^\n\r]*/gi,
      ""
    );

    // Remove excessive whitespace.
    cleaned = cleaned.replace(
      /[ \t]{2,}/g,
      " "
    );

    return cleaned.trim();
  };

  // =========================================================
  // GET ONLY FILE NAME
  // =========================================================
  //
  // The backend may send:
  //
  // C:\Users\hp\OneDrive\Desktop\Series3\data\documents\test\test_policy.txt
  //
  // The UI will ONLY show:
  //
  // test_policy.txt
  //
  // =========================================================

  const getFileName = (source) => {
    if (!source || typeof source !== "string") {
      return "Unknown source";
    }

    return source
      .split("\\")
      .pop()
      .split("/")
      .pop();
  };

  // =========================================================
  // GET UPDATED AT
  // =========================================================
  //
  // This value comes directly from the backend/Qdrant payload.
  //
  // Example:
  //
  // "updated_at": "2026-08-25T10:30:00"
  //
  // The UI displays the timestamp exactly as received.
  //
  // =========================================================

  const getUpdatedAt = (item) => {
    if (!item) {
      return "Unknown";
    }

    return (
      item.updated_at ||
      item.payload?.updated_at ||
      "Unknown"
    );
  };

  // =========================================================
  // SIMILARITY SCORE
  // =========================================================

  const getSimilarity = (item) => {
    if (!item) {
      return 0;
    }

    return Math.round(
      (item.similarity_score || item.score || 0) * 100
    );
  };

  // =========================================================
  // VERIFICATION DATA
  // =========================================================

  const verification = data?.verification;

  const isVerified =
    verification?.status === "verified";

  const hasEvidence =
    data?.evidence?.length > 0;

  // =========================================================
  // METRIC ANIMATION
  // =========================================================

  useEffect(() => {
    if (!data || !verification) {
      return;
    }

    const targetConfidence = Math.round(
      (verification.confidence || 0) * 100
    );

    const targetClaims =
      verification.claims?.length || 0;

    const targetEvidence =
      data.evidence?.length || 0;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (
          !entry.isIntersecting ||
          animationStarted.current
        ) {
          return;
        }

        animationStarted.current = true;

        const duration = 1000;
        const startTime = performance.now();

        const animate = (currentTime) => {
          const progress = Math.min(
            (currentTime - startTime) / duration,
            1
          );

          const easedProgress =
            1 - Math.pow(1 - progress, 3);

          setAnimatedConfidence(
            Math.round(
              targetConfidence * easedProgress
            )
          );

          setAnimatedClaims(
            Math.round(
              targetClaims * easedProgress
            )
          );

          setAnimatedEvidence(
            Math.round(
              targetEvidence * easedProgress
            )
          );

          if (progress < 1) {
            requestAnimationFrame(animate);
          }
        };

        requestAnimationFrame(animate);
      },
      {
        threshold: 0.35,
      }
    );

    if (metricsRef.current) {
      observer.observe(metricsRef.current);
    }

    return () => observer.disconnect();
  }, [data, verification]);

  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="app">

      {/* =====================================================
          HEADER
      ====================================================== */}

      <header className="header">

        <div className="brand">

          <div className="logo">
            <ShieldCheck size={25} />
          </div>

          <div>

            <h1>
              Knowledge Integrity Engine
            </h1>

            <p>
              Evidence-grounded knowledge verification
            </p>

          </div>

        </div>

        <div className="status">

          <span className="status-dot" />

          Engine Online

        </div>

      </header>

      {/* =====================================================
          MAIN
      ====================================================== */}

      <main className="container">

        {/* ===================================================
            HERO
        ==================================================== */}

        <section className="hero">

          <span className="eyebrow">
            AI KNOWLEDGE VERIFICATION
          </span>

          <h2>
            Ask your knowledge base.
            <br />
            <span>Trust the evidence.</span>
          </h2>

          <p>
            Retrieve relevant knowledge, verify claims,
            and generate evidence-grounded answers
            without unsupported facts.
          </p>

        </section>

        {/* ===================================================
            SEARCH
        ==================================================== */}

        <section className="search-card">

          <div className="input-wrapper">

            <Search size={21} />

            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about your knowledge base..."
              rows={2}
            />

            <button
              onClick={askQuestion}
              disabled={loading}
            >
              {loading
                ? "Verifying..."
                : "Ask"}
            </button>

          </div>

          <div className="examples">

            <span>
              Try:
            </span>

            <button
              onClick={() =>
                setQuestion(
                  "What must important technical decisions include?"
                )
              }
            >
              Technical decisions
            </button>

            <button
              onClick={() =>
                setQuestion(
                  "How frequently should documents be reviewed?"
                )
              }
            >
              Review frequency
            </button>

            <button
              onClick={() =>
                setQuestion(
                  "Who is responsible for approving internal engineering documentation?"
                )
              }
            >
              Documentation approval
            </button>

          </div>

        </section>

        {/* ===================================================
            ARCHITECTURE
        ==================================================== */}

        <section className="architecture-strip">

          <div>
            <Database size={17} />
            <span>
              Retrieve
            </span>
          </div>

          <span className="flow-arrow">
            →
          </span>

          <div>
            <Search size={17} />
            <span>
              Extract
            </span>
          </div>

          <span className="flow-arrow">
            →
          </span>

          <div>
            <ShieldCheck size={17} />
            <span>
              Verify
            </span>
          </div>

          <span className="flow-arrow">
            →
          </span>

          <div>
            <Sparkles size={17} />
            <span>
              Generate
            </span>
          </div>

        </section>

        {/* ===================================================
            ERROR
        ==================================================== */}

        {data?.error && (

          <div className="error-card">

            <AlertTriangle size={20} />

            <span>
              {data.error}
            </span>

          </div>

        )}

        {/* ===================================================
            RESULTS
        ==================================================== */}

        {data && !data.error && (

          <section className="results">

            {/* =================================================
                RESULT HEADER
            ================================================== */}

            <div className="result-header">

              <div>

                <span className="section-label">
                  VERIFICATION RESULT
                </span>

                <h3>
                  {data.question}
                </h3>

              </div>

              <div
                className={`verification-badge ${
                  isVerified
                    ? "verified"
                    : "unverified"
                }`}
              >

                {isVerified ? (
                  <ShieldCheck size={18} />
                ) : (
                  <AlertTriangle size={18} />
                )}

                {verification?.status
                  ? verification.status.replace(
                      "_",
                      " "
                    )
                  : "unknown"}

              </div>

            </div>

            {/* =================================================
                VERIFIED ANSWER
            ================================================== */}

            <div
              className={`answer-card ${
                isVerified
                  ? "answer-verified"
                  : "answer-unverified"
              }`}
            >

              <div className="card-title">

                {isVerified ? (
                  <CheckCircle2 size={19} />
                ) : (
                  <AlertTriangle size={19} />
                )}

                {isVerified
                  ? "Verified Answer"
                  : "Unverified Answer"}

              </div>

              <p>
                {cleanAnswer(data.answer)}
              </p>

            </div>

            {/* =================================================
                METRICS
            ================================================== */}

            <div
              className="metrics"
              ref={metricsRef}
            >

              <div className="metric">

                <span>
                  Confidence
                </span>

                <strong>
                  {animatedConfidence}%
                </strong>

              </div>

              <div className="metric">

                <span>
                  Verified claims
                </span>

                <strong>
                  {animatedClaims}
                </strong>

              </div>

              <div className="metric">

                <span>
                  Evidence results
                </span>

                <strong>
                  {animatedEvidence}
                </strong>

              </div>

            </div>

            {/* =================================================
                WARNINGS
            ================================================== */}

            {verification?.warnings?.length > 0 && (

              <div className="warning-card">

                <AlertTriangle size={20} />

                <div>

                  <strong>
                    Verification warnings
                  </strong>

                  {verification.warnings.map(
                    (warning, index) => (

                      <p key={index}>
                        {warning}
                      </p>

                    )
                  )}

                </div>

              </div>

            )}

            {/* =================================================
                NO EVIDENCE
            ================================================== */}

            {!hasEvidence && (

              <div className="empty-evidence">

                <AlertTriangle size={20} />

                <div>

                  <strong>
                    No supporting evidence found
                  </strong>

                  <p>
                    The knowledge base does not contain
                    enough evidence to verify this question.
                  </p>

                </div>

              </div>

            )}

            {/* =================================================
                EVIDENCE
            ================================================== */}

            {hasEvidence && (

              <section className="evidence-section">

                <div className="section-heading">

                  <div>

                    <span className="section-label">
                      SOURCE MATERIAL
                    </span>

                    <h3>
                      Evidence used
                    </h3>

                  </div>

                  <div className="evidence-count">

                    <span className="evidence-count-number">
                      {data.evidence.length}
                    </span>

                    <span className="evidence-count-label">
                      supporting results
                    </span>

                  </div>

                </div>

                <div className="evidence-list">

                  {data.evidence.map(
                    (item, index) => {

                      const source =
                        item.source ||
                        item.payload?.source ||
                        "";

                      const rawClaim =
                        item.claim ||
                        item.payload?.text ||
                        "No evidence text available.";

                      const claim =
                        cleanEvidenceText(
                          rawClaim
                        );

                      const similarity =
                        getSimilarity(item);

                      const updatedAt =
                        getUpdatedAt(item);

                      return (

                        <article
                          className="evidence-card"
                          key={index}
                        >

                          <div className="evidence-icon">
                            <FileText size={19} />
                          </div>

                          <div className="evidence-content">

                            <p>
                              {claim}
                            </p>

                            <div className="evidence-meta">

                              {/* SOURCE */}

                              <span className="evidence-source">

                                <span className="meta-label">
                                  Source
                                </span>

                                <span className="meta-value">
                                  {getFileName(source)}
                                </span>

                              </span>

                              {/* SIMILARITY */}

                              <span className="evidence-similarity">

                                <span className="meta-label">
                                  Similarity
                                </span>

                                <span className="meta-value">
                                  {similarity}%
                                </span>

                              </span>

                              {/* FRESHNESS */}

                              <span className="evidence-freshness">

                                <span className="meta-label">
                                  Freshness
                                </span>

                               <span className="meta-value freshness-value">
                                  {updatedAt}
                                </span>

                              </span>

                            </div>

                          </div>

                        </article>

                      );

                    }
                  )}

                </div>

              </section>

            )}

          </section>

        )}

        {/* ===================================================
            ABOUT
        ==================================================== */}

        <section className="about-section">

          <span className="section-label">
            HOW IT WORKS
          </span>

          <h3>
            Evidence before answers.
          </h3>

          <p>
            The system retrieves relevant knowledge,
            extracts claims, evaluates supporting evidence,
            and only presents information that can be
            grounded in the knowledge base.
          </p>

          <div className="about-grid">

            <div>

              <Database size={20} />

              <strong>
                Semantic retrieval
              </strong>

              <span>
                Finds relevant knowledge using vector search.
              </span>

            </div>

            <div>

              <ShieldCheck size={20} />

              <strong>
                Claim verification
              </strong>

              <span>
                Checks whether retrieved evidence supports
                the answer.
              </span>

            </div>

            <div>

              <CheckCircle2 size={20} />

              <strong>
                Confidence scoring
              </strong>

              <span>
                Shows how strongly the evidence supports
                the result.
              </span>

            </div>

          </div>

        </section>

      </main>

    </div>
  );
}

export default App;