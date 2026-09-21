"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, CheckCircle2, Download, ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";

const checklist = [
  "Risk assessment table",
  "Method statement",
  "Emergency arrangements",
  "PPE & plant requirements",
];

export function Hero() {
  return (
    <section className="relative overflow-hidden">
      {/* soft background accents */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10"
        style={{
          background:
            "radial-gradient(600px 300px at 80% 10%, rgba(245,158,11,0.08), transparent 70%), radial-gradient(600px 300px at 10% 20%, rgba(11,31,58,0.06), transparent 70%)",
        }}
      />

      <div className="mx-auto grid max-w-6xl items-center gap-12 px-6 py-16 lg:grid-cols-2 lg:py-24">
        <div>
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <Badge variant="accent">AI-assisted RAMS generation</Badge>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.08 }}
            className="mt-4 text-4xl font-bold tracking-tight text-foreground sm:text-5xl"
          >
            Generate Professional RAMS in{" "}
            <span className="text-accent">Minutes</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.16 }}
            className="mt-4 max-w-lg text-lg text-muted"
          >
            Create structured Risk Assessments and Method Statements with AI
            assistance, then download professional Word and PDF documents.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.24 }}
            className="mt-8 flex flex-wrap items-center gap-3"
          >
            <Link
              href="/register"
              className="inline-flex h-12 items-center gap-2 rounded-lg bg-accent px-6 text-base font-semibold text-accent-foreground shadow-sm transition-colors hover:bg-accent-hover"
            >
              Start Creating RAMS
              <ArrowRight className="h-4 w-4" aria-hidden />
            </Link>
            <a
              href="#how-it-works"
              className="inline-flex h-12 items-center rounded-lg border border-border bg-surface px-6 text-base font-medium transition-colors hover:bg-surface-muted"
            >
              See How It Works
            </a>
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.4 }}
            className="mt-6 flex items-center gap-2 text-sm text-muted"
          >
            <ShieldCheck className="h-4 w-4 text-success" aria-hidden />
            Draft documents for review by a competent person
          </motion.p>
        </div>

        {/* Document mockup */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="relative mx-auto w-full max-w-md"
        >
          <div className="rounded-xl border border-border bg-surface shadow-xl">
            {/* doc header */}
            <div className="flex items-center justify-between border-b border-border px-5 py-4">
              <div className="flex items-center gap-2">
                <span className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-primary-foreground">
                  <span className="text-xs font-bold">R</span>
                </span>
                <div>
                  <p className="text-xs font-semibold">RAMS-000123</p>
                  <p className="text-[10px] text-muted">Rev 01</p>
                </div>
              </div>
              <Badge variant="success">Ready</Badge>
            </div>

            {/* doc body */}
            <div className="space-y-4 px-5 py-5">
              <div>
                <p className="text-sm font-semibold text-foreground">
                  Riverside Warehouse Fit-Out
                </p>
                <p className="text-xs text-muted">
                  Northbridge Construction Ltd · Manchester
                </p>
              </div>
              <div className="space-y-2">
                {checklist.map((item) => (
                  <div key={item} className="flex items-center gap-2">
                    <CheckCircle2 className="h-3.5 w-3.5 text-success" aria-hidden />
                    <span className="text-xs text-muted">{item}</span>
                  </div>
                ))}
              </div>
              {/* risk table skeleton */}
              <div className="rounded-lg border border-border">
                <div className="grid grid-cols-4 gap-2 border-b border-border bg-surface-muted px-3 py-2 text-[10px] font-medium text-muted">
                  <span>Hazard</span>
                  <span>L</span>
                  <span>S</span>
                  <span>Risk</span>
                </div>
                {[
                  ["Working at height", "2", "4", "8"],
                  ["Manual handling", "3", "2", "6"],
                  ["Electrical work", "1", "5", "5"],
                ].map(([h, l, s, r]) => (
                  <div
                    key={h}
                    className="grid grid-cols-4 gap-2 border-b border-border px-3 py-2 text-[10px] text-muted last:border-0"
                  >
                    <span className="text-foreground">{h}</span>
                    <span>{l}</span>
                    <span>{s}</span>
                    <span className="font-semibold text-foreground">{r}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* doc footer */}
            <div className="flex justify-end gap-2 border-t border-border px-5 py-3">
              <span className="inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-[11px] font-medium text-muted">
                <Download className="h-3 w-3" aria-hidden />
                DOCX
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-md bg-primary px-2.5 py-1 text-[11px] font-medium text-primary-foreground">
                <Download className="h-3 w-3" aria-hidden />
                PDF
              </span>
            </div>
          </div>

          {/* floating chips */}
          <motion.div
            animate={{ y: [0, -6, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            className="absolute -right-4 -top-4 rounded-lg border border-border bg-surface px-3 py-2 text-xs font-medium shadow-md"
          >
            ⚡ Generated in 42s
          </motion.div>
          <motion.div
            animate={{ y: [0, 6, 0] }}
            transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
            className="absolute -bottom-4 -left-4 rounded-lg border border-border bg-surface px-3 py-2 text-xs font-medium shadow-md"
          >
            📄 Word + PDF
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
