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
              <Link to="/users" className="nav-link">
                Users
              </Link>
            </li>
          </ul>
        </nav>
      </header>

      <main className="p-4">
        <Outlet />
      </main>

      <footer className="d-flex fixed-bottom p-4 border-top bg-light">
        <span className="flex-fill">&copy; DjangoKit 2022</span>
        <Link to="/admin" className="nav-link">
          Admin
        </Link>
      </footer>
    </>
  );
}

export default Layout;
