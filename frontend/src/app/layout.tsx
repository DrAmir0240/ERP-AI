import type { Metadata } from "next";
import { AuthProvider } from "@/components/auth/auth-provider";
import "./globals.css";

export const metadata: Metadata = {
  title: "DrGame ERP",
  description: "ERP and commerce platform for DrGame",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fa" dir="rtl">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
