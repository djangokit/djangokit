import React from "react";
import { createRoot, hydrateRoot } from "react-dom/client";
import App from "./client.app";

const rootElement = document.getElementById("root");

// Hydrate server-rendered page if:
//
// 1. The project is configured to use SSR. This setting is statically
//    injected when the client bundle is built.
const PROJECT_USES_SSR = JSON.parse("{{ settings.ssr|lower }}");
//
// 2. The root element contains markup to be rendered. Note that we are
//    assuming the lack of markup is an intentional signal to disable
//    SSR hydration.
const SSR_DISABLED = !rootElement.children.length;

const HYDRATE = PROJECT_USES_SSR && !SSR_DISABLED;

if (HYDRATE) {
  hydrateRoot(rootElement, <App />);
} else {
  createRoot(rootElement).render(<App />);
}
