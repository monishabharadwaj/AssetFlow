import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import { QueryProvider } from "./app/providers/query-provider";
import { AuthProvider } from "./features/auth/auth-context";
import { AppRoutes } from "./app/router/routes";
import { ErrorBoundary } from "./shared/components/feedback/error-boundary";
import { ToastProvider } from "./shared/components/feedback/toast-provider";
import "./styles/globals.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <QueryProvider>
        <ToastProvider>
          <BrowserRouter>
            <AuthProvider>
              <AppRoutes />
            </AuthProvider>
          </BrowserRouter>
        </ToastProvider>
      </QueryProvider>
    </ErrorBoundary>
  </React.StrictMode>,
);
