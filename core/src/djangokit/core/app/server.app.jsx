import React from "react";

import { createStaticRouter, StaticRouterProvider } from "react-router";

import routes from "./routes";
import Auth from "./server.auth";
import SharedWrapper from "./wrapper";
import Wrapper from "./server.wrapper";

const location = process.argv[2] || "/";
const routerContext = { location };
const router = createStaticRouter(routes, routerContext);

export default function App() {
  return (
    <React.StrictMode>
      <Auth>
        <SharedWrapper>
          <Wrapper>
            <StaticRouterProvider router={router} context={routerContext} />
          </Wrapper>
        </SharedWrapper>
      </Auth>
    </React.StrictMode>
  );
}
