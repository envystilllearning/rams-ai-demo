import { forwardRef, type SelectHTMLAttributes } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

export type SelectProps = SelectHTMLAttributes<HTMLSelectElement> & {
  error?: string;
};

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, error, children, ...props }, ref) => (
    <div className="relative">
      <select
        ref={ref}
        aria-invalid={Boolean(error) || undefined}
        className={cn(
          "h-10 w-full appearance-none rounded-lg border bg-surface px-3 pr-9 text-sm text-foreground",
          "transition-colors duration-150",
          "disabled:cursor-not-allowed disabled:opacity-50",
          error ? "border-danger" : "border-border",
          className
        )}
        {...props}
      >
        {children}
      </select>
      <ChevronDown
        className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted"
        aria-hidden
      />
    </div>
  )
);
Select.displayName = "Select";
