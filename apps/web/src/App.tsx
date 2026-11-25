import { AGENT_TYPES } from "@toth/shared";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { Link, Route, Routes } from "react-router";

import { Button } from "@/components/ui/button";

function HomePage() {
  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-4 p-8">
      <h1 className="text-3xl font-semibold">Toth Research</h1>
      <p>{AGENT_TYPES.length} specialized agents</p>
      <div>
        <Button disabled>Start analysis</Button>
      </div>
    </main>
  );
}

function NotFoundPage() {
  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-4 p-8">
      <p className="text-xl">Page not found</p>
      <Link to="/" className="underline">
        Back to home
      </Link>
    </main>
  );
}

export default function App() {
  const [queryClient] = useState(() => new QueryClient());
  return (
    <QueryClientProvider client={queryClient}>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </QueryClientProvider>
  );
}
