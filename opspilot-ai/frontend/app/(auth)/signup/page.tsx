"use client";

import Link from "next/link";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/common/Button";
import { FormField } from "@/components/common/FormField";
import { useAuth } from "@/hooks/useAuth";
import { ApiError } from "@/lib/api";
import { SignupFormValues, signupSchema } from "@/lib/validations";

export default function SignupPage() {
  const { register: registerUser } = useAuth();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignupFormValues>({ resolver: zodResolver(signupSchema) });

  async function onSubmit(values: SignupFormValues) {
    setServerError(null);
    try {
      await registerUser(
        values.fullName,
        values.email,
        values.password,
        values.organizationName
      );
    } catch (err) {
      setServerError(err instanceof ApiError ? err.message : "Something went wrong. Try again.");
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <h1 className="font-display text-2xl font-semibold">Create your account</h1>
        <p className="mt-1.5 text-sm text-text-muted">
          You&apos;ll be the admin of your new organization.
        </p>

        <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
          <FormField
            id="fullName"
            label="Full name"
            autoComplete="name"
            error={errors.fullName?.message}
            {...register("fullName")}
          />
          <FormField
            id="organizationName"
            label="Organization name"
            placeholder="e.g. Acme Retail Co."
            error={errors.organizationName?.message}
            {...register("organizationName")}
          />
          <FormField
            id="email"
            label="Email"
            type="email"
            autoComplete="email"
            error={errors.email?.message}
            {...register("email")}
          />
          <FormField
            id="password"
            label="Password"
            type="password"
            autoComplete="new-password"
            error={errors.password?.message}
            {...register("password")}
          />

          {serverError && <p className="text-sm text-status-danger">{serverError}</p>}

          <Button type="submit" loading={isSubmitting}>
            Create account
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-text-muted">
          Already have an account?{" "}
          <Link href="/login" className="text-accent-cyan hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </main>
  );
}
