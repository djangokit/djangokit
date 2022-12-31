import React from "react";
import ReactDOMServer from "react-dom/server";
import App from "./server.app";

const html = ReactDOMServer.renderToString(<App />);

console.log(html.trim());
