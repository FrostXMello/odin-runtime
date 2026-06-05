import type { Metadata } from "next";
import { Providers } from "./providers";
import { OperatorShell } from "@/components/layout/operator-shell";
import "./globals.css";

export const metadata: Metadata = {
  title: "ODIN Operator — Runtime Control",
  description: "Odin AI runtime observability and orchestration console",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>
        <Providers>
          <OperatorShell>{children}</OperatorShell>
        </Providers>
      </body>
    </html>
  );
}
