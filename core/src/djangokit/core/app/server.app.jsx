import React from "react";

import {
  unstable_createStaticRouter,
  unstable_StaticRouterProvider as RouterProvider,
} from "react-router-dom/server";

import routes from "./routes";
import Auth from "./server.auth";
import SharedWrapper from "./wrapper";
import Wrapper from "./server.wrapper";

const location = process.argv[2] || "/";
const routerContext = { location };
const router = unstable_createStaticRouter(routes, routerContext);

export default function App() {
  return (
    <React.StrictMode>
      <Auth>
        <SharedWrapper>
          <Wrapper>
            <RouterProvider router={router} context={routerContext} />
          </Wrapper>
        </SharedWrapper>
      </Auth>
    </React.StrictMode>
  );
}
