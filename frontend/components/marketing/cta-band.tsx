import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { FadeIn } from "@/components/marketing/fade-in";

export function CtaBand() {
  return (
    <section className="py-20">
      <div className="mx-auto max-w-6xl px-6">
        <FadeIn>
          <div className="rounded-2xl bg-primary px-8 py-14 text-center text-primary-foreground">
            <h2 className="text-3xl font-bold tracking-tight">
              Ready to write your next RAMS in minutes?
            </h2>
            <p className="mx-auto mt-3 max-w-xl opacity-80">
              Join contractors who stopped wrestling with templates and started
              generating structured documents on demand.
            </p>
            <Link
              href="/register"
              className="mt-8 inline-flex h-12 items-center gap-2 rounded-lg bg-accent px-6 text-base font-semibold text-accent-foreground shadow-sm transition-colors hover:bg-accent-hover"
            >
              Start Creating RAMS
              <ArrowRight className="h-4 w-4" aria-hidden />
            </Link>
          </div>
        </FadeIn>
      </div>
    </section>
  );
}
