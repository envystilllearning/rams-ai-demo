"use client";

import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";
import { createClient } from "@/lib/supabase/client";

export function LogoutButton() {
  const router = useRouter();

  async function onLogout() {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/login");
    router.refresh();
  }

  return (
    <button
      onClick={onLogout}
      className="inline-flex h-9 items-center gap-2 rounded-lg px-3 text-sm text-muted transition-colors hover:bg-surface-muted hover:text-foreground"
    >
      <LogOut className="h-4 w-4" aria-hidden />
      Log out
    </button>
  );
}
