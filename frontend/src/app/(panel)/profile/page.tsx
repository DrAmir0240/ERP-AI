import { ProfileForm } from "@/components/auth/profile-form";
import { PanelShell } from "@/components/layout/panel-shell";

export default function ProfilePage() {
  return (
    <PanelShell title="پروفایل کاربر" description="اطلاعات حساب و نقش‌های فعال کاربر از API احراز هویت Core دریافت می‌شود.">
      <ProfileForm />
    </PanelShell>
  );
}
