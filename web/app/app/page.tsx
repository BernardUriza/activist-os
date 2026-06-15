import { Suspense } from "react";

import { AppClient } from "./AppClient";

export const metadata = {
  title: "Coordination Console",
};

export default function AppPage() {
  return (
    <Suspense fallback={<div className="p-8 text-app-muted">Loading Activist OS…</div>}>
      <AppClient />
    </Suspense>
  );
}
