export default function Header() {
  return (
    <header className="header">
      <div className="header-inner">
        <div className="logo">
          <span className="logo-text">Korean Cars</span>
        </div>
        <nav className="nav">
          <a href="#cars" className="nav-link">Catalog</a>
        </nav>
      </div>
    </header>
  );
}