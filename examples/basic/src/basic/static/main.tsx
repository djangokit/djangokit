import React from "react";
import ReactDOM from "react-dom/client";

import { createBrowserRouter, RouterProvider } from "react-router-dom";

import { default as Layout_root } from "../routes/layout";

import { default as Page_root } from "../routes/page";

import { default as Page__id } from "../routes/_id/page";

import { default as Layout_admin } from "../routes/admin/layout";
import { default as Page_admin } from "../routes/admin/page";

import { default as Page_users } from "../routes/users/page";
import { default as Page_users__id } from "../routes/users/_id/page";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout_root />,
    children: [
      {
        element: <Page_root data={{}} />,
      },
      {
        path: ":id",
        element: <Page__id data={{}} />,
      },
      {
        path: "users",
        children: [
          {
            element: <Page_users data={{}} />,
          },
          {
            path: ":id",
            element: <Page_users__id data={{}} />,
          },
        ],
      },
    ],
  },

  {
    path: "/admin",
    element: <Layout_admin />,
    children: [
      {
        element: <Page_admin data={{}} />,
      },
    ],
  },
]);

const rootElement = document.getElementById("root");

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
