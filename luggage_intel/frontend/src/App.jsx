import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend
} from 'recharts';
import {
  Search, Award, TrendingUp, CheckCircle2, AlertCircle,
  ExternalLink, Truck, Star, ThumbsUp, DollarSign,
  Layers, MessageSquare, Zap, RefreshCw, Check, Info, Tag, ArrowRight
} from 'lucide-react';

const SUGGESTIONS = [
  "Sony WH-1000XM4 Noise Cancelling",
  "OnePlus Nord CE 4",
  "Philips Digital Air Fryer 4.1L",
  "Green Soul Ergonomic Office Chair",
  "Samsung Galaxy Watch 6",
  "Instant Pot Duo 6 Quart"
];

function App() {
  const [query, setQuery] = useState('');
  const [maxBudget, setMaxBudget] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [comparisonData, setComparisonData] = useState(null);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'comparison' | 'analytics' | 'tester'

  // Live tester state
  const [liveReview, setLiveReview] = useState('');
  const [liveResult, setLiveResult] = useState(null);
  const [testingReview, setTestingReview] = useState(false);

  // Perform an initial search on mount so the page isn't empty
  useEffect(() => {
    handleSearch(SUGGESTIONS[0]);
  }, []);

  const handleSearch = async (searchQuery) => {
    const q = searchQuery || query;
    if (!q.trim()) return;

    setLoading(true);
    setLoadingStep(1);
    setQuery(q);

    const stepTimer1 = setTimeout(() => setLoadingStep(2), 700);
    const stepTimer2 = setTimeout(() => setLoadingStep(3), 1500);

    try {
      const res = await axios.post('http://localhost:5000/api/search', {
        query: q,
        maxBudget: maxBudget ? parseFloat(maxBudget) : undefined
      });
      setComparisonData(res.data);
    } catch (err) {
      console.error("Search failed", err);
      alert("Failed to compare products. Please ensure the backend server is running on port 5000.");
    } finally {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      setLoading(false);
      setLoadingStep(0);
    }
  };

  const handleLiveAnalyze = async () => {
    if (!liveReview.trim()) return;
    setTestingReview(true);
    setLiveResult(null);
    try {
      const res = await axios.post('http://localhost:5000/api/analyze', { review: liveReview });
      setLiveResult(res.data);
    } catch (err) {
      console.error("Live analysis failed", err);
      alert("Failed to analyze review.");
    } finally {
      setTestingReview(false);
    }
  };

  const winner = comparisonData?.winner;
  const runnerUps = comparisonData?.runner_ups || [];
  const platforms = comparisonData?.platform_comparison || [];
  const aspects = comparisonData?.aspect_ratings || [];
  const insights = comparisonData?.strategic_insights || [];
  const formatPrice = (price) => price == null ? 'Unavailable' : `₹${Number(price).toLocaleString('en-IN')}`;
  const formatRating = (rating) => rating == null ? 'Unavailable' : `${rating} / 5`;

  return (
    <div className="app-layout">
      {/* Navigation Header */}
      <header className="main-header">
        <div className="header-content">
          <div className="brand-logo">
            <div className="logo-icon">
              <Tag size={18} />
            </div>
            <div>
              <h1 className="brand-title">SmartBuy AI</h1>
              <span className="brand-tagline">Find the best real deal, across every store that has it</span>
            </div>
          </div>

          <div className="live-status-pill">
            <span className="pulse-dot" /> Live retailer data
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="dashboard-container">
        {/* Search Hero Box */}
        <section className="search-hero glass-panel">
          <div className="search-intro">
            <h2>Find the best real deal on anything</h2>
            <p>We check live listings across retailers and compare price, rating, and reviews to find the strongest match.</p>
          </div>

          <form 
            className="search-form" 
            onSubmit={(e) => { e.preventDefault(); handleSearch(); }}
          >
            <div className="search-input-wrapper">
              <Search className="search-icon" size={20} />
              <input 
                type="text" 
                className="main-search-input"
                placeholder="Search any product (e.g. Trolley Bag 65cm, Sony Headphones, Air Fryer, iPhone 15)..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>

            <div className="budget-input-wrapper">
              <span className="currency-prefix">₹</span>
              <input 
                type="number" 
                className="budget-input"
                placeholder="Max budget"
                value={maxBudget}
                onChange={(e) => setMaxBudget(e.target.value)}
              />
            </div>

            <button 
              type="submit" 
              className="search-btn"
              disabled={loading || !query.trim()}
            >
              {loading ? (
                <>
                  <RefreshCw className="spin" size={18} />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <span>Compare & Find Best</span>
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>

          {/* Search Suggestion Pills */}
          <div className="suggestion-pills">
            <span className="suggestion-label">Try searching:</span>
            {SUGGESTIONS.map((s, idx) => (
              <button 
                key={idx} 
                className="pill-btn"
                onClick={() => handleSearch(s)}
                disabled={loading}
              >
                {s}
              </button>
            ))}
          </div>
        </section>

        {/* Loading Progress State */}
        {loading && (
          <div className="loading-state glass-panel">
            <div className="loading-spinner-ring" />
            <div className="loading-text">
              <h3>Looking this up for you</h3>
              <p>
                {loadingStep === 1 && "Checking listings across retailers..."}
                {loadingStep === 2 && "Comparing prices, ratings, and reviews..."}
                {loadingStep === 3 && "Picking the best match..."}
              </p>
            </div>
          </div>
        )}

        {/* Results View */}
        {!loading && comparisonData && (
          <>
            {/* Navigation Tabs */}
            <div className="tab-navigation">
              <button
                className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                <Award size={16} /> Best Match
              </button>
              <button
                className={`tab-btn ${activeTab === 'comparison' ? 'active' : ''}`}
                onClick={() => setActiveTab('comparison')}
              >
                <Layers size={16} /> Compare All
              </button>
              <button
                className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
                onClick={() => setActiveTab('analytics')}
              >
                <TrendingUp size={16} /> Charts
              </button>
              <button
                className={`tab-btn ${activeTab === 'tester' ? 'active' : ''}`}
                onClick={() => setActiveTab('tester')}
              >
                <MessageSquare size={16} /> Review Tester
              </button>
            </div>

            {/* TAB 1: OVERVIEW & WINNER SPOTLIGHT */}
            {activeTab === 'overview' && winner && (
              <div className="overview-container">
                {/* Winner card */}
                <div className="winner-card glass-panel highlight-gold">
                  <div className="winner-badge-ribbon">
                    <Award size={15} /> Best match for this search
                  </div>

                  <div className="winner-layout">
                    <div className="winner-main-info">
                      <div className="winner-store-tag">
                        <span>Best Deal On</span>
                        <strong>{winner.best_platform}</strong>
                      </div>

                      <h2 className="winner-title">{winner.title}</h2>
                      <p className="winner-headline">"{winner.verdict_headline}"</p>

                      <div className="price-box">
                        <div className="price-main">
                          <span className="price-amount">{formatPrice(winner.best_price)}</span>
                        </div>
                        {winner.mrp && (
                          <div className="mrp-wrapper">
                            <span className="mrp-strike">MRP ₹{winner.mrp?.toLocaleString('en-IN')}</span>
                            <span className="discount-tag">{winner.discount_pct}% OFF</span>
                          </div>
                        )}
                      </div>

                      {/* Score Metrics Grid */}
                      <div className="kpi-grid">
                        <div className="kpi-item">
                          <div className="kpi-icon"><Star size={16} color="#D9A441" /></div>
                          <div>
                            <div className="kpi-val">{formatRating(winner.rating)}</div>
                            <div className="kpi-lbl">{winner.review_count == null ? 'No verified reviews' : `${winner.review_count} Reviews`}</div>
                          </div>
                        </div>

                        <div className="kpi-item">
                          <div className="kpi-icon"><ThumbsUp size={16} color="#2F9E64" /></div>
                          <div>
                            <div className="kpi-val">{winner.discount_pct == null ? 'Unavailable' : `${winner.discount_pct}% OFF`}</div>
                            <div className="kpi-lbl">Discount vs MRP</div>
                          </div>
                        </div>

                        <div className="kpi-item">
                          <div className="kpi-icon"><Zap size={16} color="#E85D4C" /></div>
                          <div>
                            <div className="kpi-val">{winner.match_score == null ? 'Unavailable' : `${winner.match_score}/100`}</div>
                            <div className="kpi-lbl">Match Score (price + rating + reviews)</div>
                          </div>
                        </div>
                      </div>

                      {/* Tags / Badges */}
                      {winner.tags && winner.tags.length > 0 && (
                        <div className="theme-pills" style={{ margin: '0.5rem 0 1rem' }}>
                          {winner.tags.map((tag, i) => (
                            <span key={i} className="theme-pill"><Tag size={12} style={{ marginRight: 4 }} />{tag}</span>
                          ))}
                        </div>
                      )}

                      {/* Why Buy Rationale */}
                      <div className="why-buy-box">
                        <h4>Why this one</h4>
                        <p>{winner.why_buy}</p>
                      </div>

                      {/* Pros & Cons */}
                      <div className="pros-cons-grid">
                        <div className="pros-box">
                          <h5><CheckCircle2 size={16} color="#2F9E64" /> Key Strengths</h5>
                          <ul>
                            {winner.pros?.map((pro, i) => (
                              <li key={i}><Check size={14} className="pro-check" /> {pro}</li>
                            ))}
                          </ul>
                        </div>

                        {winner.cons && winner.cons.length > 0 && (
                          <div className="cons-box">
                            <h5><AlertCircle size={16} color="#C97A1F" /> Keep in Mind</h5>
                            <ul>
                              {winner.cons.map((con, i) => (
                                <li key={i}><Info size={14} className="con-info" /> {con}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>

                      {/* Delivery info -- only shown when the retailer actually provided it */}
                      {winner.warranty_delivery && (
                        <div className="perks-row">
                          <div className="perk-badge">
                            <Truck size={14} /> {winner.warranty_delivery}
                          </div>
                        </div>
                      )}

                      {/* Big CTA Button */}
                      <div className="action-row">
                        <a 
                          href={winner.buy_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="buy-winner-btn"
                        >
                          <span>{winner.best_price == null ? 'Open retailer search' : `Buy Now on ${winner.best_platform} at ${formatPrice(winner.best_price)}`}</span>
                          <ExternalLink size={20} />
                        </a>
                      </div>
                    </div>
                  </div>
                </div>

                {/* RUNNER-UP CARDS */}
                {runnerUps.length > 0 && (
                  <div className="runner-ups-section">
                    <h3>Other options worth a look</h3>
                    <div className="runner-grid">
                      {runnerUps.map((runner, idx) => (
                        <div key={idx} className="glass-panel runner-card">
                          <div className="runner-category-tag">{runner.category}</div>
                          <h4>{runner.title}</h4>
                          <p className="runner-highlight">{runner.highlight}</p>
                          <div className="runner-meta">
                            <div className="runner-price">{formatPrice(runner.price)}</div>
                            <div className="runner-platform">on {runner.platform}</div>
                          </div>
                          <a 
                            href={runner.buy_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="runner-btn"
                          >
                            View on {runner.platform} <ExternalLink size={14} />
                          </a>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* STRATEGIC SHOPPING INSIGHTS */}
                {insights.length > 0 && (
                  <div className="glass-panel insights-panel">
                    <h3>Good to know</h3>
                    <ul className="insights-list">
                      {insights.map((insight, idx) => (
                        <li key={idx}>
                          <span className="insight-num">{idx + 1}</span>
                          <p>{insight}</p>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* TAB 2: 5-PLATFORM COMPARISON MATRIX */}
            {activeTab === 'comparison' && (
              <div className="comparison-tab-container">
                <div className="glass-panel table-panel">
                  <div className="table-header">
                    <h3>All listings found</h3>
                    <p>Every live listing found for this search, with real price, rating, and tags/badges.</p>
                  </div>

                  <div className="responsive-table-wrapper">
                    <table className="comparison-table">
                      <thead>
                        <tr>
                          <th>Platform</th>
                          <th>Product Name</th>
                          <th>Price (INR)</th>
                          <th>Rating & Reviews</th>
                          <th>Tags</th>
                          <th>Deal Status</th>
                          <th>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {platforms.map((p, idx) => (
                          <tr key={idx} className={p.best_deal_here ? 'best-deal-row' : ''}>
                            <td>
                              <div className="platform-name-cell">
                                <span className={`platform-badge ${p.platform.toLowerCase().replace(/\s+/g, '')}`}>
                                  {p.platform}
                                </span>
                              </div>
                            </td>
                            <td className="product-title-cell">{p.product_name}</td>
                            <td className="price-cell">
                              <strong>{formatPrice(p.price)}</strong>
                              {p.discount_pct && <span className="table-discount">({p.discount_pct}% off)</span>}
                            </td>
                            <td>
                              <div className="table-rating">
                                <Star size={14} fill="#D9A441" stroke="none" />
                                <span>{p.rating == null ? 'Unavailable' : p.rating}</span>
                                {p.review_count != null && <small>({p.review_count})</small>}
                              </div>
                            </td>
                            <td>
                              {p.tags && p.tags.length > 0 ? (
                                <div className="theme-pills">
                                  {p.tags.slice(0, 2).map((tag, i) => (
                                    <span key={i} className="theme-pill">{tag}</span>
                                  ))}
                                </div>
                              ) : (
                                <span style={{ color: 'var(--text-muted)' }}>—</span>
                              )}
                            </td>
                            <td>
                              {p.best_deal_here ? (
                                <span className="best-deal-badge"><Award size={12} /> Best match</span>
                              ) : (
                                <span className="standard-deal-badge">{p.scrape_status === 'blocked' ? 'Blocked' : p.price == null ? 'Unavailable' : 'Available'}</span>
                              )}
                            </td>
                            <td>
                              <a
                                href={p.product_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="table-buy-btn"
                              >
                                View Deal <ExternalLink size={12} />
                              </a>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 3: DEEP ANALYTICS & CHARTS */}
            {activeTab === 'analytics' && (
              <div className="analytics-tab-container grid grid-cols-2">
                {/* Price Comparison Bar Chart */}
                <div className="glass-panel">
                  <h3><DollarSign size={18} /> Price by retailer</h3>
                  <div className="chart-container">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={platforms}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                        <XAxis dataKey="platform" stroke="#94a3b8" />
                        <YAxis stroke="#94a3b8" />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '8px' }}
                          formatter={(value) => [formatPrice(value), 'Price']}
                        />
                        <Legend />
                        <Bar dataKey="price" name="Price (₹)" fill="#38bdf8" radius={[6, 6, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Rating Comparison */}
                <div className="glass-panel">
                  <h3><ThumbsUp size={18} /> Rating by retailer</h3>
                  <div className="chart-container">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={platforms}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                        <XAxis dataKey="platform" stroke="#94a3b8" />
                        <YAxis domain={[0, 5]} stroke="#94a3b8" />
                        <Tooltip
                          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '8px' }}
                          formatter={(value) => [`${value}★`, 'Rating']}
                        />
                        <Legend />
                        <Bar dataKey="rating" name="Rating (out of 5)" fill="#22c55e" radius={[6, 6, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Aspect-Level Quality Scores */}
                {aspects.length > 0 && (
                  <div className="glass-panel" style={{ gridColumn: 'span 2' }}>
                    <h3><Award size={18} /> Quality breakdown</h3>
                    <div className="aspects-bar-list">
                      {aspects.map((asp, idx) => (
                        <div key={idx} className="aspect-bar-row">
                          <div className="aspect-name">{asp.aspect}</div>
                          <div className="aspect-track">
                            <div 
                              className="aspect-fill" 
                              style={{ width: `${asp.score}%` }} 
                            />
                          </div>
                          <div className="aspect-score-label">{asp.score}/100</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB 4: LIVE REVIEW TESTER */}
            {activeTab === 'tester' && (
              <div className="tester-tab-container">
                <div className="glass-panel">
                  <h3><MessageSquare size={18} /> Try the review analyzer</h3>
                  <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
                    Paste any custom review from Amazon, Flipkart, or offline retail to test real-time sentiment polarity and theme extraction.
                  </p>

                  <div className="tester-layout">
                    <textarea 
                      className="glass-input"
                      rows={5}
                      placeholder="Paste or write a customer review here (e.g. 'The bag is extremely durable and wheels glide smoothly, but zipper feels slightly cheap')..."
                      value={liveReview}
                      onChange={(e) => setLiveReview(e.target.value)}
                    />

                    <button 
                      className="search-btn"
                      onClick={handleLiveAnalyze}
                      disabled={testingReview || !liveReview.trim()}
                      style={{ marginTop: '0.75rem', alignSelf: 'flex-start' }}
                    >
                      {testingReview ? 'Analyzing with Llama 3...' : 'Analyze Sentiment Live'}
                    </button>

                    {liveResult && (
                      <div className="tester-result-box glass-panel">
                        <h4>Analysis Output</h4>
                        <div className="tester-metrics">
                          <div>
                            <span className="lbl">Sentiment Label:</span>
                            <strong className={`tag-${liveResult.sentiment_label?.toLowerCase()}`}>
                              {liveResult.sentiment_label}
                            </strong>
                          </div>
                          <div>
                            <span className="lbl">Sentiment Polarity Score:</span>
                            <strong>{liveResult.sentiment_score}</strong>
                          </div>
                          <div>
                            <span className="lbl">Key Extracted Themes:</span>
                            <div className="theme-pills">
                              {liveResult.key_themes?.map((th, i) => (
                                <span key={i} className="theme-pill">{th}</span>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="main-footer">
        <p>SmartBuy AI — Real-time price, rating, and review comparison across Indian e-commerce retailers.</p>
      </footer>
    </div>
  );
}

export default App;
