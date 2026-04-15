"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import {
  clearAuthSession,
  fetchCurrentUser,
  getStoredToken,
  getStoredUser,
  hasRequiredRole,
  persistAuthSession,
} from "./auth";

export function useRequireRole(allowedRoles, options = {}) {
  const router = useRouter();
  const normalizedAllowedRoles = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];
  const rolesKey = normalizedAllowedRoles.join("|");
  const {
    unauthenticatedRedirect = "/login",
    unauthorizedRedirect = "/products",
  } = options;

  const [user, setUser] = useState(() => {
    const cachedUser = getStoredUser();
    return cachedUser && hasRequiredRole(cachedUser, normalizedAllowedRoles)
      ? cachedUser
      : null;
  });
  const [token, setToken] = useState(() => getStoredToken());
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  useEffect(() => {
    const allowedRoleList = rolesKey.split("|").filter(Boolean);
    const storedToken = getStoredToken();
    const cachedUser = getStoredUser();

    setIsCheckingAuth(true);

    if (!storedToken || !cachedUser) {
      clearAuthSession();
      setUser(null);
      setToken(null);
      setIsCheckingAuth(false);
      router.replace(unauthenticatedRedirect);
      return;
    }

    if (!hasRequiredRole(cachedUser, allowedRoleList)) {
      setUser(null);
      setToken(storedToken);
      setIsCheckingAuth(false);
      router.replace(unauthorizedRedirect);
      return;
    }

    setUser(cachedUser);
    setToken(storedToken);

    let isCancelled = false;

    async function validateSession() {
      try {
        const currentUser = await fetchCurrentUser(storedToken);
        if (isCancelled) {
          return;
        }

        if (!hasRequiredRole(currentUser, allowedRoleList)) {
          setUser(null);
          router.replace(unauthorizedRedirect);
          return;
        }

        persistAuthSession({
          access_token: storedToken,
          user: currentUser,
        });
        setUser(currentUser);
        setToken(storedToken);
      } catch {
        if (isCancelled) {
          return;
        }

        clearAuthSession();
        setUser(null);
        setToken(null);
        router.replace(unauthenticatedRedirect);
      } finally {
        if (!isCancelled) {
          setIsCheckingAuth(false);
        }
      }
    }

    validateSession();

    return () => {
      isCancelled = true;
    };
  }, [rolesKey, router, unauthenticatedRedirect, unauthorizedRedirect]);

  return {
    user,
    token,
    isCheckingAuth,
  };
}
