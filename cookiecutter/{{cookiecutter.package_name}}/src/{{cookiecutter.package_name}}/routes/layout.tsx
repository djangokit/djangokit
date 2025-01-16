/* Root Layout */

import { Link, Outlet } from "react-router";

export default function Layout() {
  return (
    <>
      <header className="p-4 bg-dark text-light">
        <nav>
          <Link to="/" className="text-light text-decoration-none">
            Home
          </Link>
        </nav>
      </header>

      <main className="p-4">
        <Outlet />
      </main>

      <footer className="p-4 border-top">&copy; {{ cookiecutter.package_name }}</footer>
    </>
  );
}
