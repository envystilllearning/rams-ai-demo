import { Clock, FileText, FileDown, ShieldCheck } from "lucide-react";
import { FadeIn } from "@/components/marketing/fade-in";

const stats = [
  { icon: Clock, value: "Minutes", label: "To a complete draft RAMS" },
  { icon: FileText, value: "Structured", label: "Hazards, controls & method statement" },
  { icon: FileDown, value: "2 formats", label: "Word + PDF, every time" },
  { icon: ShieldCheck, value: "Reviewed", label: "Drafts for competent person approval" },
];

export function StatsBand() {
  return (
    <section className="bg-primary py-14 text-primary-foreground">
      <div className="mx-auto grid max-w-6xl grid-cols-2 gap-8 px-6 lg:grid-cols-4">
        {stats.map((s, i) => (
          <FadeIn key={s.label} delay={i * 0.08}>
            <div className="flex flex-col items-center gap-2 text-center">
              <s.icon className="h-6 w-6 opacity-80" aria-hidden />
              <p className="text-2xl font-bold">{s.value}</p>
              <p className="text-sm opacity-80">{s.label}</p>
            </div>
          </FadeIn>
        ))}
      </div>
    </section>
  );
}
