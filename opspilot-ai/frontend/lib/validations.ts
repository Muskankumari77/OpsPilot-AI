import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("Enter a valid email address."),
  password: z.string().min(1, "Enter your password."),
});
export type LoginFormValues = z.infer<typeof loginSchema>;

export const signupSchema = z.object({
  fullName: z.string().min(1, "Enter your name."),
  organizationName: z.string().min(1, "Name your organization."),
  email: z.string().email("Enter a valid email address."),
  password: z.string().min(8, "Password must be at least 8 characters."),
});
export type SignupFormValues = z.infer<typeof signupSchema>;
