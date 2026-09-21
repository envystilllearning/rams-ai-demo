"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { FileText, Menu, X } from "lucide-react";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { cn } from "@/lib/utils";

const links = [
  { href: "#features", label: "Features" },
  { href: "#how-it-works", label: "How it works" },
  { href: "#pricing", label: "Pricing" },
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    function onScroll() {
      setScrolled(window.scrollY > 8);
    }
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={cn(
        "sticky top-0 z-40 border-b transition-all duration-200",
        scrolled
          ? "border-border bg-surface/80 backdrop-blur-md"
          : "border-transparent bg-transparent"
      )}
    >
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <FileText className="h-4.5 w-4.5" aria-hidden />
          </span>
          <span className="font-bold tracking-tight">RAMS AI</span>
        </Link>

        <nav className="hidden items-center gap-7 text-sm text-muted md:flex" aria-label="Main">
          {links.map((l) => (
            <a key={l.href} href={l.href} className="transition-colors hover:text-foreground">
              {l.label}
            </a>
          ))}
        </nav>

        <div className="hidden items-center gap-2 md:flex">
          <ThemeToggle />
          <Link
            href="/login"
            className="inline-flex h-8 items-center rounded-lg px-3 text-sm font-medium transition-colors hover:bg-surface-muted"
          >
            Login
          </Link>
          <Link
            href="/register"
            className="inline-flex h-8 items-center rounded-lg bg-accent px-3 text-sm font-semibold text-accent-foreground shadow-sm transition-colors hover:bg-accent-hover"
          >
            Get Started
          </Link>
        </div>

        <button
          className="rounded-lg p-2 text-muted md:hidden"
          onClick={() => setOpen(!open)}
          aria-label={open ? "Close menu" : "Open menu"}
          aria-expanded={open}
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {open && (
        <nav
          className="border-t border-border bg-surface px-6 py-4 md:hidden"
          aria-label="Mobile"
        >
          <div className="flex flex-col gap-4 text-sm">
            {links.map((l) => (
              <a key={l.href} href={l.href} onClick={() => setOpen(false)}>
                {l.label}
              </a>
            ))}
            <div className="flex items-center justify-between pt-2">
              <div className="flex gap-2">
                <Link
                  href="/login"
                  className="inline-flex h-8 items-center rounded-lg border border-border px-3 text-sm font-medium"
                  onClick={() => setOpen(false)}
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="inline-flex h-8 items-center rounded-lg bg-accent px-3 text-sm font-semibold text-accent-foreground"
                  onClick={() => setOpen(false)}
                >
                  Get Started
                </Link>
              </div>
              <ThemeToggle />
            </div>
          </div>
        </nav>
      )}
    </header>
  );
}
