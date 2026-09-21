"use client";

import {
  createContext,
  useCallback,
  useContext,
  useRef,
  useState,
} from "react";
import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, Info, X, XCircle } from "lucide-react";

type ToastVariant = "info" | "success" | "danger";
type Toast = { id: number; title: string; description?: string; variant: ToastVariant };

const ToastContext = createContext<{
  toast: (t: { title: string; description?: string; variant?: ToastVariant }) => void;
} | null>(null);

const icons: Record<ToastVariant, React.ElementType> = {
  info: Info,
  success: CheckCircle2,
  danger: XCircle,
};

const colors: Record<ToastVariant, string> = {
  info: "text-info",
  success: "text-success",
  danger: "text-danger",
};

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const idRef = useRef(0);

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const toast = useCallback(
    ({
      title,
      description,
      variant = "info",
    }: {
      title: string;
      description?: string;
      variant?: ToastVariant;
    }) => {
      const id = ++idRef.current;
      setToasts((prev) => [...prev, { id, title, description, variant }]);
      setTimeout(() => dismiss(id), 5000);
    },
    [dismiss]
  );

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div
        aria-live="polite"
        className="fixed bottom-4 right-4 z-50 flex w-80 flex-col gap-2"
      >
        <AnimatePresence>
          {toasts.map((t) => {
            const Icon = icons[t.variant];
            return (
              <motion.div
                key={t.id}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 8 }}
                transition={{ duration: 0.2 }}
                className="flex items-start gap-3 rounded-xl border border-border bg-surface p-4 shadow-lg"
              >
                <Icon className={`mt-0.5 h-5 w-5 shrink-0 ${colors[t.variant]}`} aria-hidden />
                <div className="flex-1 text-sm">
                  <p className="font-medium text-foreground">{t.title}</p>
                  {t.description && (
                    <p className="mt-0.5 text-muted">{t.description}</p>
                  )}
                </div>
                <button
                  onClick={() => dismiss(t.id)}
                  aria-label="Dismiss notification"
                  className="text-muted transition-colors hover:text-foreground"
                >
                  <X className="h-4 w-4" aria-hidden />
                </button>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
