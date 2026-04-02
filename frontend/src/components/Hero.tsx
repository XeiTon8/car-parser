export default function Hero() {
  return (
    <section className="hero">
      <div className="hero-bg">
        <div className="hero-grid" aria-hidden="true">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="hero-grid-line" />
          ))}
        </div>
      </div>
      <div className="hero-content">
        <p className="hero-eyebrow">Direct from Korea</p>
        <h1 className="hero-title">
          Find Your
          <br />
          <em>Next Car</em>
        </h1>
        <p className="hero-desc">
          Real-time listings from Encar.com — Korea's largest used car
          marketplace. Updated daily.
        </p>
        <div className="hero-stats">
          <div className="stat">
            <span className="stat-value">150k+</span>
            <span className="stat-label">Active listings</span>
          </div>
          <div className="stat-divider" />
          <div className="stat">
            <span className="stat-value">Daily</span>
            <span className="stat-label">Price updates</span>
          </div>
          <div className="stat-divider" />
          <div className="stat">
            <span className="stat-value">USD</span>
            <span className="stat-label">Prices converted</span>
          </div>
        </div>
        <a href="#cars" className="hero-cta">
          Browse Catalog
          <span className="hero-cta-arrow">→</span>
        </a>
      </div>
    </section>
  );
}