import { AlertTriangle, CheckCircle2, Info, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

type AlertVariant = "info" | "success" | "warning" | "danger";

const config: Record<
  AlertVariant,
  { icon: React.ElementType; className: string }
> = {
  info: { icon: Info, className: "bg-info-soft text-info" },
  success: { icon: CheckCircle2, className: "bg-success-soft text-success" },
  warning: { icon: AlertTriangle, className: "bg-warning-soft text-warning" },
  danger: { icon: XCircle, className: "bg-danger-soft text-danger" },
};

export function Alert({
  variant = "info",
  title,
  children,
  className,
}: {
  variant?: AlertVariant;
  title?: string;
  children?: React.ReactNode;
  className?: string;
}) {
  const { icon: Icon, className: iconBg } = config[variant];
  return (
    <div
      role="alert"
      className={cn("flex gap-3 rounded-lg p-4", iconBg, className)}
    >
      <Icon className="mt-0.5 h-5 w-5 shrink-0" aria-hidden />
      <div className="text-sm">
        {title && <p className="font-semibold">{title}</p>}
        {children && <div className="mt-0.5 opacity-90">{children}</div>}
      </div>
    </div>
  );
}
