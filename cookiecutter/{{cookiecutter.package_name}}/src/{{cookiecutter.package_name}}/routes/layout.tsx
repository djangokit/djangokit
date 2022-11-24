/* Root Layout */

import { Link, Outlet } from "react-router-dom";

function Layout() {
  return (
    <>
      <header>
        <nav>
          <Link to="/">
            Home
          </Link>
        </nav>
      </header>

      <main>
        <Outlet />
      </main>

      <footer>&copy; {{ cookiecutter.package_name }}</footer>
    </>
  );
}

export default Layout;
