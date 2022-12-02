import React from "react";
import { createRoot, hydrateRoot } from "react-dom/client";
import App from "./client.app";

const SSR = JSON.parse("{{ settings.ssr|lower }}");

const rootElement = document.getElementById("root");

if (SSR) {
  hydrateRoot(rootElement, <App />);
} else {
  createRoot(rootElement).render(<App />);
}
