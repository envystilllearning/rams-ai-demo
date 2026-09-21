import Link from "next/link";
import { FileText } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-border bg-surface">
      <div className="mx-auto max-w-6xl px-6 py-12">
        <div className="flex flex-col gap-8 md:flex-row md:justify-between">
          <div className="max-w-sm">
            <div className="flex items-center gap-2.5">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                <FileText className="h-4.5 w-4.5" aria-hidden />
              </span>
              <span className="font-bold tracking-tight">RAMS AI</span>
            </div>
            <p className="mt-4 text-sm leading-relaxed text-muted">
              AI-assisted Risk Assessments and Method Statements for UK
              construction contractors.
            </p>
          </div>

          <nav
            className="grid grid-cols-2 gap-x-12 gap-y-2 text-sm"
            aria-label="Footer"
          >
            <a href="#features" className="text-muted transition-colors hover:text-foreground">
              Features
            </a>
            <a href="#pricing" className="text-muted transition-colors hover:text-foreground">
              Pricing
            </a>
            <Link href="/login" className="text-muted transition-colors hover:text-foreground">
              Login
            </Link>
            <Link href="/register" className="text-muted transition-colors hover:text-foreground">
              Get Started
            </Link>
          </nav>
        </div>

        <div className="mt-10 rounded-lg bg-surface-muted p-4">
          <p className="text-xs leading-relaxed text-muted">
            <strong className="text-foreground">Disclaimer:</strong> This
            application provides AI-assisted draft RAMS content. Generated
            documents must be reviewed, amended where necessary, and approved by
            a competent person before being used on a live project. This is a
            demo product; terms and privacy pages are placeholders.
          </p>
        </div>

        <div className="mt-6 flex flex-col items-center justify-between gap-2 text-xs text-muted sm:flex-row">
          <p>© {new Date().getFullYear()} RAMS AI Demo. All rights reserved.</p>
          <div className="flex gap-4">
            <Link href="/terms" className="transition-colors hover:text-foreground">
              Terms
            </Link>
            <Link href="/privacy" className="transition-colors hover:text-foreground">
              Privacy
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
