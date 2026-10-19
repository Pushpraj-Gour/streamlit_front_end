import { useId } from "react";
import { cn } from "@/lib/utils";

const control =
  "w-full rounded-xl border border-line bg-surface px-4 text-[15px] text-ink placeholder:text-muted/70 " +
  "transition-colors hover:border-ink/25 focus:border-accent focus:outline-none";

interface FieldProps {
  label: string;
  hint?: string;
  error?: string;
  optional?: boolean;
  children: (id: string) => React.ReactNode;
}

export function Field({ label, hint, error, optional, children }: FieldProps) {
  const id = useId();
  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="flex items-baseline justify-between text-sm font-medium">
        {label}
        {optional && <span className="text-xs font-normal text-muted">Optional</span>}
      </label>
      {children(id)}
      {error ? (
        <p className="text-xs text-danger">{error}</p>
      ) : (
        hint && <p className="text-xs text-muted">{hint}</p>
      )}
    </div>
  );
}

export function Input({ className, ...rest }: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input className={cn(control, "h-11", className)} {...rest} />;
}

export function Textarea({ className, ...rest }: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={cn(control, "min-h-24 py-3 leading-relaxed", className)} {...rest} />;
}

export function Select({ className, children, ...rest }: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select className={cn(control, "h-11", className)} {...rest}>
      {children}
    </select>
  );
}
