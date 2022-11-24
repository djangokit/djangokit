import { Outlet } from "react-router-dom";

export default function NestedLayout() {
  return (
    <div className="d-flex">
      <div>
        <h2>Left</h2>
      </div>
      <div>
        <h2>Right</h2>
        <Outlet />
      </div>
    </div>
  );
}
