/* Admin Layout */

import { Outlet } from "react-router-dom";

export default function Layout() {
  return (
    <>
      <header>Admin</header>
      <main>
        <Outlet />
      </main>
    </>
  );
}
