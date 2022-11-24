/* Root Layout */

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
              <Link to="/docs" className="nav-link">
                Docs
              </Link>
            </li>
            <li className="nav-item">
              <a href="https://github.com/djangokit" className="nav-link">
                Code
              </a>
            </li>
          </ul>
        </nav>
      </header>

      <main className="p-4">
        <Outlet />
      </main>

      <footer className="d-flex fixed-bottom p-4 border-top bg-light">
        <span className="flex-fill">&copy; DjangoKit 2022</span>
      </footer>
    </>
  );
}

export default Layout;
