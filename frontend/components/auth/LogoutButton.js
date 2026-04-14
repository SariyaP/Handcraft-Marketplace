"use client";

import { useRouter } from "next/navigation";

import { clearAuthSession } from "../../lib/auth";

export default function LogoutButton({ className = "ghost-button", redirectTo = "/login" }) {
  const router = useRouter();

  function handleLogout() {
    clearAuthSession();
    router.replace(redirectTo);
  }

  return (
    <button className={className} type="button" onClick={handleLogout}>
      Log Out
    </button>
  );
}
