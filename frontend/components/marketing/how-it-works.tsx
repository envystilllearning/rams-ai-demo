import { ClipboardList, Sparkles, FileCheck } from "lucide-react";
import { SectionHeading } from "@/components/ui/section-heading";
import { FadeIn } from "@/components/marketing/fade-in";

const steps = [
  {
    number: "01",
    icon: ClipboardList,
    title: "Enter project details",
    description:
      "Fill in a simple 4-step form: project, work description, controls and review.",
  },
  {
    number: "02",
    icon: Sparkles,
    title: "Generate your RAMS",
    description:
      "AI drafts the risk assessment and method statement from your information.",
  },
  {
    number: "03",
    icon: FileCheck,
    title: "Review and download",
    description:
      "Get a professional Word document and PDF, ready for approval and site use.",
  },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="scroll-mt-20 py-20">
      <div className="mx-auto max-w-6xl px-6">
        <SectionHeading
          eyebrow="How it works"
          title="From project details to professional document"
          description="Three steps. No template wrangling, no formatting — just the content."
        />
        <div className="grid gap-6 md:grid-cols-3">
          {steps.map((s, i) => (
            <FadeIn key={s.number} delay={i * 0.1}>
              <div className="relative rounded-xl border border-border bg-surface p-6">
                <span className="text-4xl font-bold text-border" aria-hidden>
                  {s.number}
                </span>
                <div className="mt-4 inline-flex rounded-lg bg-accent p-2.5 text-accent-foreground">
                  <s.icon className="h-5 w-5" aria-hidden />
                </div>
                <h3 className="mt-3 font-semibold text-foreground">{s.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted">
                  {s.description}
                </p>
              </div>
            </FadeIn>
          ))}
        </div>
      </div>
    </section>
  );
}
