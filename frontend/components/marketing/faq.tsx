"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { SectionHeading } from "@/components/ui/section-heading";
import { cn } from "@/lib/utils";

const faqs = [
  {
    q: "What is a RAMS document?",
    a: "RAMS stands for Risk Assessment and Method Statement — a document that sets out the hazards of a job, the controls to manage them, and the step-by-step method for carrying out the work safely.",
  },
  {
    q: "Are the generated documents legally compliant?",
    a: "No. RAMS AI produces draft documents to assist you. Every generated RAMS must be reviewed, amended where necessary, and approved by a competent person before being used on a live project.",
  },
  {
    q: "What formats do I receive?",
    a: "Each RAMS is delivered as a professionally formatted Word document (.docx) and a matching PDF, stored securely in your account and available for download at any time.",
  },
  {
    q: "Do I need to re-enter my company details every time?",
    a: "No. You save your company information and logo once in your profile, and every RAMS you create is pre-filled with it automatically.",
  },
  {
    q: "Can I cancel my subscription?",
    a: "Yes. You can manage or cancel your subscription at any time from the billing page in your dashboard via the customer portal.",
  },
];

export function Faq() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section className="bg-surface-muted/50 py-20">
      <div className="mx-auto max-w-3xl px-6">
        <SectionHeading
          eyebrow="FAQ"
          title="Frequently asked questions"
        />
        <div className="space-y-3">
          {faqs.map((f, i) => {
            const open = openIndex === i;
            return (
              <div
                key={f.q}
                className="overflow-hidden rounded-xl border border-border bg-surface"
              >
                <button
                  className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
                  onClick={() => setOpenIndex(open ? null : i)}
                  aria-expanded={open}
                >
                  <span className="text-sm font-medium text-foreground">{f.q}</span>
                  <ChevronDown
                    className={cn(
                      "h-4 w-4 shrink-0 text-muted transition-transform duration-200",
                      open && "rotate-180"
                    )}
                    aria-hidden
                  />
                </button>
                {open && (
                  <p className="border-t border-border px-5 py-4 text-sm leading-relaxed text-muted">
                    {f.a}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
