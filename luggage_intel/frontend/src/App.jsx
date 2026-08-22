import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';
import { 
  Search, ShoppingBag, Award, TrendingUp, CheckCircle2, AlertCircle, 
  ExternalLink, ShieldCheck, Truck, Sparkles, Star, ThumbsUp, DollarSign, 
  Layers, MessageSquare, ArrowRight, Zap, RefreshCw, Check, Info
} from 'lucide-react';

const SUGGESTIONS = [
  "Safari Thorium Trolley Bag 65cm",
  "Sony WH-1000XM4 Noise Cancelling",
  "OnePlus Nord CE 4",
  "Philips Digital Air Fryer 4.1L",
  "Green Soul Ergonomic Office Chair",
  "American Tourister Ivy Trolley Bag"
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

  // Perform initial search on mount with a great default
  useEffect(() => {
    handleSearch("Safari Thorium Trolley Bag 65cm");
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

  return (
    <div className="app-layout">
      {/* Background Decorative Glows */}
      <div className="bg-glow bg-glow-1" />
      <div className="bg-glow bg-glow-2" />

      {/* Navigation Header */}
      <header className="main-header">
        <div className="header-content">
          <div className="brand-logo">
            <div className="logo-icon">
              <Sparkles size={22} />
            </div>
            <div>
              <h1 className="brand-title">SmartBuy AI</h1>
              <span className="brand-tagline">Multi-Platform E-Commerce Intelligence & Best-Deal Recommender</span>
            </div>
          </div>

          <div className="platform-badges-header">
            <div className="live-status-pill">
              <span className="pulse-dot" /> Live Market Scraper
            </div>
            <span className="platform-pill amazon">Amazon</span>
            <span className="platform-pill flipkart">Flipkart</span>
            <span className="platform-pill croma">Croma</span>
            <span className="platform-pill reliance">Reliance Digital</span>
            <span className="platform-pill tatacliq">Tata CLiQ</span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="dashboard-container">
        {/* Search Hero Box */}
        <section className="search-hero glass-panel">
          <div className="search-intro">
            <h2>Search Any Product & Find the #1 Best Deal to Buy</h2>
            <p>Our AI scans top 5 e-commerce platforms, analyzes prices, user reviews, sentiment & defects to crown the ultimate winner.</p>
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
                placeholder="Max Budget (Optional)"
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
                  <Sparkles size={18} />
                  <span>Compare & Find Best</span>
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
              <h3>AI Market Intelligence In Progress</h3>
              <p>
                {loadingStep === 1 && "1/3 Searching catalogs across Amazon, Flipkart, Croma, Reliance Digital & Tata CLiQ..."}
                {loadingStep === 2 && "2/3 Extracting verified user reviews, rating consistency & pricing spread..."}
                {loadingStep === 3 && "3/3 Groq Llama 3.3 MCDM Engine ranking sentiment, durability & value for money..."}
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
                <Award size={18} /> #1 Top Recommendation
              </button>
              <button 
                className={`tab-btn ${activeTab === 'comparison' ? 'active' : ''}`}
                onClick={() => setActiveTab('comparison')}
              >
                <Layers size={18} /> 5-Platform Comparison Matrix
              </button>
              <button 
                className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
                onClick={() => setActiveTab('analytics')}
              >
                <TrendingUp size={18} /> Deep Analytics & Charts
              </button>
              <button 
                className={`tab-btn ${activeTab === 'tester' ? 'active' : ''}`}
                onClick={() => setActiveTab('tester')}
              >
                <MessageSquare size={18} /> Live Review Tester
              </button>
            </div>

            {/* TAB 1: OVERVIEW & #1 WINNER SPOTLIGHT */}
            {activeTab === 'overview' && winner && (
              <div className="overview-container">
                {/* 🏆 THE WINNER CARD */}
                <div className="winner-card glass-panel highlight-gold">
                  <div className="winner-badge-ribbon">
                    <Award size={18} /> #1 BEST OVERALL CHOICE TO BUY
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
                          <span className="price-symbol">₹</span>
                          <span className="price-amount">{winner.best_price?.toLocaleString('en-IN')}</span>
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
                          <div className="kpi-icon"><Star size={16} color="#fbbf24" /></div>
                          <div>
                            <div className="kpi-val">{winner.rating} / 5</div>
                            <div className="kpi-lbl">{winner.review_count} Reviews</div>
                          </div>
                        </div>

                        <div className="kpi-item">
                          <div className="kpi-icon"><ThumbsUp size={16} color="#22c55e" /></div>
                          <div>
                            <div className="kpi-val">{winner.positive_sentiment_pct || 88}% Positive</div>
                            <div className="kpi-lbl">AI Sentiment Score</div>
                          </div>
                        </div>

                        <div className="kpi-item">
                          <div className="kpi-icon"><Zap size={16} color="#60a5fa" /></div>
                          <div>
                            <div className="kpi-val">{winner.value_score || 95}/100</div>
                            <div className="kpi-lbl">Value-for-Money Index</div>
                          </div>
                        </div>
                      </div>

                      {/* Why Buy Rationale */}
                      <div className="why-buy-box">
                        <h4><Sparkles size={16} /> Why This is the #1 Recommended Pick:</h4>
                        <p>{winner.why_buy}</p>
                      </div>

                      {/* Pros & Cons */}
                      <div className="pros-cons-grid">
                        <div className="pros-box">
                          <h5><CheckCircle2 size={16} color="#22c55e" /> Key Strengths</h5>
                          <ul>
                            {winner.pros?.map((pro, i) => (
                              <li key={i}><Check size={14} className="pro-check" /> {pro}</li>
                            ))}
                          </ul>
                        </div>

                        {winner.cons && winner.cons.length > 0 && (
                          <div className="cons-box">
                            <h5><AlertCircle size={16} color="#f59e0b" /> Keep in Mind</h5>
                            <ul>
                              {winner.cons.map((con, i) => (
                                <li key={i}><Info size={14} className="con-info" /> {con}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>

                      {/* Warranty & Delivery Badges */}
                      <div className="perks-row">
                        <div className="perk-badge">
                          <ShieldCheck size={16} /> {winner.warranty_delivery || "1 Year Brand Warranty"}
                        </div>
                        <div className="perk-badge">
                          <Truck size={16} /> Fast Verified Store Delivery
                        </div>
                      </div>

                      {/* Big CTA Button */}
                      <div className="action-row">
                        <a 
                          href={winner.buy_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="buy-winner-btn"
                        >
                          <span>Buy Now on {winner.best_platform} at ₹{winner.best_price?.toLocaleString('en-IN')}</span>
                          <ExternalLink size={20} />
                        </a>
                      </div>
                    </div>
                  </div>
                </div>

                {/* RUNNER-UP CARDS */}
                {runnerUps.length > 0 && (
                  <div className="runner-ups-section">
                    <h3>Alternative Category Picks</h3>
                    <div className="runner-grid">
                      {runnerUps.map((runner, idx) => (
                        <div key={idx} className="glass-panel runner-card">
                          <div className="runner-category-tag">{runner.category}</div>
                          <h4>{runner.title}</h4>
                          <p className="runner-highlight">{runner.highlight}</p>
                          <div className="runner-meta">
                            <div className="runner-price">₹{runner.price?.toLocaleString('en-IN')}</div>
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
                    <h3><Sparkles size={20} /> AI Strategic Shopping Insights for "{comparisonData.query}"</h3>
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
                    <h3>Multi-Platform Direct Comparison Matrix</h3>
                    <p>Compare exact price, delivery, and user sentiment across all 5 leading Indian retail platforms.</p>
                  </div>

                  <div className="responsive-table-wrapper">
                    <table className="comparison-table">
                      <thead>
                        <tr>
                          <th>Platform</th>
                          <th>Product Name</th>
                          <th>Price (INR)</th>
                          <th>Rating & Reviews</th>
                          <th>Positive Sentiment</th>
                          <th>Delivery Speed</th>
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
                              <strong>₹{p.price?.toLocaleString('en-IN')}</strong>
                              {p.discount_pct && <span className="table-discount">({p.discount_pct}% off)</span>}
                            </td>
                            <td>
                              <div className="table-rating">
                                <Star size={14} fill="#fbbf24" stroke="none" />
                                <span>{p.rating}</span>
                                <small>({p.review_count})</small>
                              </div>
                            </td>
                            <td>
                              <div className="sentiment-bar-wrapper">
                                <div className="sentiment-bar-fill" style={{ width: `${p.positive_sentiment_pct}%` }} />
                                <span className="sentiment-bar-text">{p.positive_sentiment_pct}%</span>
                              </div>
                            </td>
                            <td>{p.delivery_speed}</td>
                            <td>
                              {p.best_deal_here ? (
                                <span className="best-deal-badge">🏆 Lowest Price</span>
                              ) : (
                                <span className="standard-deal-badge">Available</span>
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
                  <h3><DollarSign size={20} /> Multi-Store Price Comparison (INR)</h3>
                  <div className="chart-container">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={platforms}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                        <XAxis dataKey="platform" stroke="#94a3b8" />
                        <YAxis stroke="#94a3b8" />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '8px' }}
                          formatter={(value) => [`₹${value.toLocaleString('en-IN')}`, 'Price']}
                        />
                        <Legend />
                        <Bar dataKey="price" name="Price (₹)" fill="#38bdf8" radius={[6, 6, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Positive Sentiment % Comparison */}
                <div className="glass-panel">
                  <h3><ThumbsUp size={20} /> Customer Positive Sentiment (%)</h3>
                  <div className="chart-container">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={platforms}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                        <XAxis dataKey="platform" stroke="#94a3b8" />
                        <YAxis domain={[0, 100]} stroke="#94a3b8" />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '8px' }}
                          formatter={(value) => [`${value}%`, 'Positive Reviews']}
                        />
                        <Legend />
                        <Bar dataKey="positive_sentiment_pct" name="Positive Sentiment %" fill="#22c55e" radius={[6, 6, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Aspect-Level Quality Scores */}
                {aspects.length > 0 && (
                  <div className="glass-panel" style={{ gridColumn: 'span 2' }}>
                    <h3><Award size={20} /> Aspect-Level Quality Breakdown</h3>
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
                  <h3><MessageSquare size={20} /> Live Customer Review Sentiment Analyzer</h3>
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
        <p>SmartBuy AI — Powered by Groq LLM Multi-Criteria Decision Model. Real-time comparison across India's top 5 e-commerce platforms.</p>
      </footer>
    </div>
  );
}

export default App;
