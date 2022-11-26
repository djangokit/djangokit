import React from "react";
import { createRoot, hydrateRoot } from "react-dom/client";
import App from "./client-app";

// Set this to false to do client side rendering.
const SSR = true;

const rootElement = document.getElementById("root");

if (SSR) {
  hydrateRoot(rootElement, <App />);
} else {
  createRoot(rootElement).render(<App />);
}
