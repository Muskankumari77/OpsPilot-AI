import { forwardRef, InputHTMLAttributes } from "react";

interface FormFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export const FormField = forwardRef<HTMLInputElement, FormFieldProps>(
  ({ label, error, id, ...rest }, ref) => {
    return (
      <div>
        <label htmlFor={id} className="mb-1.5 block text-sm text-text-muted">
          {label}
        </label>

        <input
          ref={ref}
          id={id}
          className="w-full rounded-lg border border-border bg-background-surface px-3.5 py-2.5 text-sm text-text-primary outline-none transition-colors focus:border-accent-indigo"
          {...rest}
        />

        {error && (
          <p className="mt-1.5 text-sm text-status-danger">
            {error}
          </p>
        )}
      </div>
    );
  }
);

FormField.displayName = "FormField";