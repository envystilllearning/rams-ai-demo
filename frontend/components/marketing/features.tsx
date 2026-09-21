import { CloudUpload, FileDown, RefreshCcw, Sparkles } from "lucide-react";
import { SectionHeading } from "@/components/ui/section-heading";
import { Card, CardContent } from "@/components/ui/card";
import { FadeIn } from "@/components/marketing/fade-in";

const features = [
  {
    icon: Sparkles,
    title: "AI-assisted generation",
    description:
      "Enter your project details once and let AI draft hazards, controls and method statements in a structured format.",
  },
  {
    icon: FileDown,
    title: "Word & PDF downloads",
    description:
      "Every RAMS is delivered as a professionally formatted Word document and matching PDF, ready to review and share.",
  },
  {
    icon: CloudUpload,
    title: "Secure cloud storage",
    description:
      "Your documents are stored safely in the cloud, available whenever you need them — survive restarts and new sessions.",
  },
  {
    icon: RefreshCcw,
    title: "Reusable company information",
    description:
      "Save your company details and logo once. Every future RAMS is pre-filled automatically.",
  },
];

export function Features() {
  return (
    <section id="features" className="scroll-mt-20 bg-surface-muted/50 py-20">
      <div className="mx-auto max-w-6xl px-6">
        <SectionHeading
          eyebrow="Features"
          title="Everything you need for professional RAMS"
          description="Built for UK construction contractors who create method statements repeatedly and value reliability and speed."
        />
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((f, i) => (
            <FadeIn key={f.title} delay={i * 0.08}>
              <Card className="h-full transition-shadow duration-200 hover:shadow-md">
                <CardContent>
                  <div className="mb-4 inline-flex rounded-lg bg-primary p-2.5 text-primary-foreground">
                    <f.icon className="h-5 w-5" aria-hidden />
                  </div>
                  <h3 className="font-semibold text-foreground">{f.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted">
                    {f.description}
                  </p>
                </CardContent>
              </Card>
            </FadeIn>
          ))}
        </div>
      </div>
    </section>
  );
}
