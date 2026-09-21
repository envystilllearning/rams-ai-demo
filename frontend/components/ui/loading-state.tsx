import { Loader2 } from "lucide-react";

export function LoadingState({
  label = "Loading...",
  className,
}: {
  label?: string;
  className?: string;
}) {
  return (
    <div
      className={`flex flex-col items-center justify-center gap-3 p-8 ${className ?? ""}`}
    >
      <Loader2 className="h-6 w-6 animate-spin text-muted" aria-hidden />
      <p className="text-sm text-muted">{label}</p>
    </div>
  );
}
