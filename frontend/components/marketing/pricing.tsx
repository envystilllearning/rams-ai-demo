import Link from "next/link";
import { Check } from "lucide-react";
import { SectionHeading } from "@/components/ui/section-heading";
import { FadeIn } from "@/components/marketing/fade-in";

const included = [
  "Unlimited RAMS*",
  "Word + PDF downloads",
  "Secure cloud storage",
  "Reusable company profile",
  "AI-assisted hazards & controls",
];

export function Pricing() {
  return (
    <section id="pricing" className="scroll-mt-20 bg-surface-muted/50 py-20">
      <div className="mx-auto max-w-6xl px-6">
        <SectionHeading
          eyebrow="Pricing"
          title="Simple, predictable pricing"
          description="One plan. Everything included. Cancel anytime from your dashboard."
        />
        <FadeIn className="mx-auto max-w-md">
          <div className="overflow-hidden rounded-2xl border-2 border-accent bg-surface shadow-lg">
            <div className="bg-accent px-6 py-2 text-center text-xs font-semibold uppercase tracking-wider text-accent-foreground">
              Most popular
            </div>
            <div className="p-8">
              <p className="text-sm font-medium text-muted">Professional</p>
              <p className="mt-2">
                <span className="text-4xl font-bold text-foreground">£9.95</span>
                <span className="text-muted"> / month</span>
              </p>
              <ul className="mt-6 space-y-3">
                {included.map((item) => (
                  <li key={item} className="flex items-center gap-2.5 text-sm">
                    <span className="flex h-5 w-5 items-center justify-center rounded-full bg-success-soft text-success">
                      <Check className="h-3 w-3" aria-hidden />
                    </span>
                    <span className="text-foreground">{item}</span>
                  </li>
                ))}
              </ul>
              <Link
                href="/register"
                className="mt-8 flex h-11 items-center justify-center rounded-lg bg-accent text-sm font-semibold text-accent-foreground shadow-sm transition-colors hover:bg-accent-hover"
              >
                Start Subscription
              </Link>
              <p className="mt-4 text-center text-xs text-muted">
                *Demo fair-use policy may apply.
              </p>
            </div>
          </div>
        </FadeIn>
      </div>
    </section>
  );
}
