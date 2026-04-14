"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import AuthShell from "../../components/auth/AuthShell";
import FormField from "../../components/auth/FormField";
import FormMessage from "../../components/auth/FormMessage";
import SubmitButton from "../../components/auth/SubmitButton";
import {
  getRedirectPathForRole,
  getStoredUser,
  loginUser,
  persistAuthSession,
} from "../../lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [values, setValues] = useState({
    email: "",
    password: "",
  });
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const storedUser = getStoredUser();
    if (storedUser?.role) {
      router.replace(getRedirectPathForRole(storedUser.role));
    }
  }, [router]);

  function handleChange(event) {
    const { name, value } = event.target;
    setValues((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setIsLoading(true);
    setErrorMessage("");

    try {
      const payload = await loginUser(values);
      persistAuthSession(payload);
      router.replace(getRedirectPathForRole(payload.user.role));
    } catch (error) {
      setErrorMessage(error.message || "Login failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <AuthShell
      eyebrow="Welcome Back"
      title="Sign in to your workshop account"
      description="Use your registered email and password to access the marketplace dashboard for your role."
      footer={
        <p>
          Need an account? <Link href="/register">Create one here</Link>.
        </p>
      }
    >
      <form className="auth-form" onSubmit={handleSubmit}>
        <FormField
          label="Email"
          name="email"
          type="email"
          value={values.email}
          onChange={handleChange}
          placeholder="maker@example.com"
          autoComplete="email"
          disabled={isLoading}
          required
        />
        <FormField
          label="Password"
          name="password"
          type="password"
          value={values.password}
          onChange={handleChange}
          placeholder="Enter your password"
          autoComplete="current-password"
          disabled={isLoading}
          required
          minLength={8}
          maxLength={128}
        />
        <FormMessage message={errorMessage} />
        <SubmitButton isLoading={isLoading} loadingLabel="Signing In...">
          Sign In
        </SubmitButton>
      </form>
    </AuthShell>
  );
}
