import { Link, Outlet } from "react-router-dom";

function Layout() {
  return (
    <>
      <header className="p-4 border-bottom bg-light">
        <nav className="navbar navbar-expand bg-light">
          <Link to="/" className="navbar-brand">
            Home
          </Link>
          <ul className="navbar-nav">
            <li className="nav-item">
              <Link to="/x" className="nav-link">
                X
              </Link>
            </li>
            <li className="nav-item">
              <Link to="/y" className="nav-link">
                Y
              </Link>
            </li>
          </ul>
        </nav>
      </header>

      <main className="p-4">
        <Outlet />
      </main>

      <footer className="fixed-bottom p-4 border-top bg-light">Footer</footer>
    </>
  );
}

export default Layout;
