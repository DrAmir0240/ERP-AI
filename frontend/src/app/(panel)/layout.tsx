import { ProtectedRoute } from "@/components/auth/protected-route";

export default function PanelLayout({ children }: { children: React.ReactNode }) {
  return <ProtectedRoute>{children}</ProtectedRoute>;
}
