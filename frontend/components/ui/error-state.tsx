import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function ErrorState({
  title = "Something went wrong",
  message,
  onRetry,
  className,
}: {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}) {
  return (
    <div
      role="alert"
      className={cn(
        "flex flex-col items-center justify-center gap-3 rounded-xl border border-border bg-surface p-10 text-center",
        className
      )}
    >
      <div className="rounded-full bg-danger-soft p-3 text-danger">
        <AlertTriangle className="h-6 w-6" aria-hidden />
      </div>
      <p className="font-medium text-foreground">{title}</p>
      {message && <p className="max-w-sm text-sm text-muted">{message}</p>}
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          <RefreshCw className="h-4 w-4" aria-hidden />
          Try again
        </Button>
      )}
    </div>
  );
}
