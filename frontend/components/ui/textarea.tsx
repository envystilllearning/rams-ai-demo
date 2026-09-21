import { forwardRef, type TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export type TextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & {
  error?: string;
};

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, error, ...props }, ref) => (
    <textarea
      ref={ref}
      aria-invalid={Boolean(error) || undefined}
      className={cn(
        "min-h-24 w-full rounded-lg border bg-surface px-3 py-2 text-sm text-foreground",
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
Textarea.displayName = "Textarea";
