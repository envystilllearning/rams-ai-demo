import Link from "next/link";
import { ArrowLeft, Clock } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function ComingSoon({ title }: { title: string }) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-border">
        <div className="mx-auto flex h-16 max-w-6xl items-center px-6">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm text-muted transition-colors hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" aria-hidden />
            Back to home
          </Link>
        </div>
      </header>

      <main className="flex flex-1 items-center justify-center px-6 py-20">
        <div className="max-w-md text-center">
          <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary text-primary-foreground">
            <Clock className="h-8 w-8" aria-hidden />
          </div>
          <Badge variant="accent" className="mb-4">
            Coming Soon
          </Badge>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            {title}
          </h1>
          <p className="mt-3 leading-relaxed text-muted">
            This page is part of the RAMS AI demo and is currently under
            development. Check back soon, or head back to the landing page to
            explore what&apos;s coming.
          </p>
          <Link
            href="/"
            className="mt-8 inline-flex h-11 items-center justify-center rounded-lg bg-accent px-6 text-sm font-semibold text-accent-foreground shadow-sm transition-colors hover:bg-accent-hover"
          >
            Explore Features
          </Link>
        </div>
      </main>

      <footer className="border-t border-border py-6 text-center text-xs text-muted">
        © {new Date().getFullYear()} RAMS AI Demo
      </footer>
    </div>
  );
}
