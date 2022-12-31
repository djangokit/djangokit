import { CookiesProvider } from "react-cookie";
import React from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import routes from "./routes";
import Auth from "./client.auth";
import SharedWrapper from "./wrapper";
import Wrapper from "./client.wrapper";

const router = createBrowserRouter(routes);

export default function App() {
  return (
    <React.StrictMode>
      <CookiesProvider>
        <Auth>
          <SharedWrapper>
            <Wrapper>
              <RouterProvider router={router} />
            </Wrapper>
          </SharedWrapper>
        </Auth>
      </CookiesProvider>
    </React.StrictMode>
  );
}
