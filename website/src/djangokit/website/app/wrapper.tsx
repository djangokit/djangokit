import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import SSRProvider from "react-bootstrap/SSRProvider";

const queryClient = new QueryClient();

export default function Wrapper({ children }) {
  return (
    <QueryClientProvider client={queryClient}>
      <SSRProvider>{children}</SSRProvider>
    </QueryClientProvider>
  );
}
