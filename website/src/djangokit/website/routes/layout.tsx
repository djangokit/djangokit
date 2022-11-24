import { Link, Outlet } from "react-router-dom";

function Layout() {
  return (
    <>
      <header>
        <nav>
          <Link to="/">Home</Link>
        </nav>
      </header>

      <main>
        <Outlet />
      </main>

      <footer>&copy; DjangoKit</footer>
    </>
  );
}

export default Layout;
