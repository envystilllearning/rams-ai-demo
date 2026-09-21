import { cn } from "@/lib/utils";

type BadgeVariant = "neutral" | "success" | "warning" | "danger" | "info" | "accent";

const styles: Record<BadgeVariant, string> = {
  neutral: "bg-surface-muted text-muted",
  success: "bg-success-soft text-success",
  warning: "bg-warning-soft text-warning",
  danger: "bg-danger-soft text-danger",
  info: "bg-info-soft text-info",
  accent: "bg-accent text-accent-foreground",
};

export function Badge({
  variant = "neutral",
  className,
  children,
}: {
  variant?: BadgeVariant;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        styles[variant],
        className
      )}
    >
      {children}
    </span>
  );
}

/** Maps RAMS/subscription statuses to badge variants (PRD §18). */
const statusMap: Record<string, BadgeVariant> = {
  // RAMS statuses
  draft: "neutral",
  generating: "info",
  ready: "success",
  failed: "danger",
  // Subscription statuses (PRD §4)
  active: "success",
  trialing: "info",
  past_due: "warning",
  canceled: "neutral",
  unpaid: "danger",
  incomplete: "danger",
  incomplete_expired: "danger",
};

export function StatusBadge({ status }: { status: string }) {
  const variant = statusMap[status] ?? "neutral";
  return (
    <Badge variant={variant}>
      {status.replace(/_/g, " ")}
    </Badge>
  );
}
