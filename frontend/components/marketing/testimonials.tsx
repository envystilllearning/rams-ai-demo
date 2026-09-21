import { Quote } from "lucide-react";
import { SectionHeading } from "@/components/ui/section-heading";
import { Card, CardContent } from "@/components/ui/card";
import { FadeIn } from "@/components/marketing/fade-in";

const testimonials = [
  {
    quote:
      "What used to take me a full evening of template editing now takes minutes. The structure is exactly what our clients expect to see.",
    name: "James Whitfield",
    role: "Contracts Manager",
    company: "Northbridge Construction Ltd",
    initials: "JW",
  },
  {
    quote:
      "My company details are saved once and every document comes out on our letterhead style. The Word and PDF outputs look genuinely professional.",
    name: "Sarah Okafor",
    role: "Site Supervisor",
    company: "Riverside Property Group",
    initials: "SO",
  },
  {
    quote:
      "The hazard sections give our team a strong starting point. We still review everything properly — but the blank-page problem is completely gone.",
    name: "Daniel Marsh",
    role: "Director",
    company: "Marsh & Sons Building",
    initials: "DM",
  },
];

export function Testimonials() {
  return (
    <section className="py-20">
      <div className="mx-auto max-w-6xl px-6">
        <SectionHeading
          eyebrow="Testimonials"
          title="Trusted by contractors who repeat this work weekly"
          description="Fictional testimonials for this demo project."
        />
        <div className="grid gap-6 md:grid-cols-3">
          {testimonials.map((t, i) => (
            <FadeIn key={t.name} delay={i * 0.1}>
              <Card className="h-full">
                <CardContent>
                  <Quote className="h-5 w-5 text-accent" aria-hidden />
                  <p className="mt-3 text-sm leading-relaxed text-foreground">
                    &ldquo;{t.quote}&rdquo;
                  </p>
                  <div className="mt-5 flex items-center gap-3">
                    <span
                      className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground"
                      aria-hidden
                    >
                      {t.initials}
                    </span>
                    <div>
                      <p className="text-sm font-medium text-foreground">{t.name}</p>
                      <p className="text-xs text-muted">
                        {t.role} · {t.company}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </FadeIn>
          ))}
        </div>
      </div>
    </section>
  );
}
