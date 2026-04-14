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
  persistAuthSession,
  registerUser,
} from "../../lib/auth";

const initialValues = {
  full_name: "",
  email: "",
  password: "",
  role: "customer",
};

export default function RegisterPage() {
  const router = useRouter();
  const [values, setValues] = useState(initialValues);
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
      const payload = await registerUser(values);
      persistAuthSession(payload);
      router.replace(getRedirectPathForRole(payload.user.role));
    } catch (error) {
      setErrorMessage(error.message || "Registration failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <AuthShell
      eyebrow="Create Account"
      title="Join the handcraft marketplace"
      description="Register as a customer to browse and commission work, or as a maker to manage your storefront."
      footer={
        <p>
          Already registered? <Link href="/login">Sign in instead</Link>.
        </p>
      }
    >
      <form className="auth-form" onSubmit={handleSubmit}>
        <FormField
          label="Full name"
          name="full_name"
          value={values.full_name}
          onChange={handleChange}
          placeholder="Ari Artisan"
          autoComplete="name"
          disabled={isLoading}
        />
        <FormField
          label="Email"
          name="email"
          type="email"
          value={values.email}
          onChange={handleChange}
          placeholder="you@example.com"
          autoComplete="email"
          disabled={isLoading}
        />
        <FormField
          label="Password"
          name="password"
          type="password"
          value={values.password}
          onChange={handleChange}
          placeholder="At least 8 characters"
          autoComplete="new-password"
          disabled={isLoading}
        />
        <FormField label="Role" name="role" disabled={isLoading}>
          <select
            id="role"
            name="role"
            value={values.role}
            onChange={handleChange}
            disabled={isLoading}
            className="form-input"
          >
            <option value="customer">Customer</option>
            <option value="maker">Maker</option>
          </select>
        </FormField>
        <FormMessage message={errorMessage} />
        <SubmitButton isLoading={isLoading} loadingLabel="Creating Account...">
          Create Account
        </SubmitButton>
      </form>
    </AuthShell>
  );
}
