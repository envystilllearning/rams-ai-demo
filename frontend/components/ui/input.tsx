import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  error?: string;
};

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, "aria-invalid": ariaInvalid, ...props }, ref) => (
    <input
      ref={ref}
      aria-invalid={ariaInvalid ?? (Boolean(error) || undefined)}
      aria-describedby={error ? `${props.id ?? props.name}-error` : undefined}
      className={cn(
        "h-10 w-full rounded-lg border bg-surface px-3 text-sm text-foreground",
        "placeholder:text-muted",
        "transition-colors duration-150",
        "disabled:cursor-not-allowed disabled:opacity-50",
        error ? "border-danger" : "border-border",
        className
      )}
      {...props}
    />
  )
);
Input.displayName = "Input";
