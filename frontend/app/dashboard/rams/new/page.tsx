"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, ArrowRight, Check, ClipboardCheck } from "lucide-react";
import { apiFetch, type Profile } from "@/lib/api";
import { createRams, EMPTY_INPUT, type RamsInput } from "@/lib/rams";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert } from "@/components/ui/alert";
import { Field } from "@/components/rams/form-field";
import { useToast } from "@/components/ui/toast";
import { cn } from "@/lib/utils";

const STEPS = ["Project", "Work", "Controls", "Review"] as const;

const LABELS: Record<keyof RamsInput, string> = {
  project_name: "Project name",
  site_address: "Site address",
  client_name: "Client",
  project_reference: "Project reference",
  start_date: "Start date",
  planned_duration: "Planned duration",
  work_description: "Work description",
  work_location: "Work location",
  materials: "Materials",
  equipment: "Equipment",
  plant: "Plant",
  tools: "Tools",
  personnel: "Personnel",
  ppe: "PPE",
  known_hazards: "Known hazards",
  site_restrictions: "Site restrictions",
  existing_controls: "Existing controls",
  emergency_info: "Emergency information",
  additional_notes: "Additional notes",
};

const STEP_FIELDS: Record<number, (keyof RamsInput)[]> = {
  0: ["project_name", "site_address", "client_name", "project_reference", "start_date", "planned_duration"],
  1: ["work_description", "work_location", "materials", "equipment", "plant", "tools", "personnel", "ppe"],
  2: ["known_hazards", "site_restrictions", "existing_controls", "emergency_info", "additional_notes"],
};

const MULTILINE: (keyof RamsInput)[] = [
  "work_description",
  "known_hazards",
  "existing_controls",
  "site_restrictions",
  "emergency_info",
  "additional_notes",
  "materials",
  "equipment",
  "plant",
  "tools",
  "personnel",
  "ppe",
];

export default function NewRamsPage() {
  const { toast } = useToast();
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [input, setInput] = useState<RamsInput>(EMPTY_INPUT);
  const [errors, setErrors] = useState<Partial<Record<keyof RamsInput, string>>>({});
  const [creating, setCreating] = useState(false);
  const [companyName, setCompanyName] = useState<string | null>(null);

  // Load company profile for the review summary
  useEffect(() => {
    apiFetch<Profile>("/api/profile")
      .then((p) => setCompanyName(p.company_name))
      .catch(() => {});
  }, []);

  function set(key: keyof RamsInput, value: string) {
    setInput((prev) => ({ ...prev, [key]: value }));
    setErrors((prev) => ({ ...prev, [key]: undefined }));
  }

  function validateStep(s: number): boolean {
    const e: Partial<Record<keyof RamsInput, string>> = {};
    if (s === 0) {
      if (input.project_name.trim().length < 3) {
        e.project_name = "Project name must be at least 3 characters";
      }
    }
    if (s === 1) {
      if (input.work_description.trim().length < 10) {
        e.work_description = "Describe the works in at least 10 characters";
      }
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  function next() {
    if (validateStep(step)) setStep((s) => Math.min(s + 1, 3));
  }

  async function onCreate() {
    if (creating) return; // duplicate-submission guard (§44)
    setCreating(true);
    try {
      const rams = await createRams(input);
      toast({
        title: "RAMS draft created",
        description: `${rams.document_number} — generation arrives in the next phase.`,
        variant: "success",
      });
      router.push(`/dashboard/rams/${rams.id}`);
    } catch (e) {
      toast({
        title: "Create failed",
        description: e instanceof Error ? e.message : "Please try again.",
        variant: "danger",
      });
      setCreating(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <Link
        href="/dashboard/rams"
        className="mb-6 inline-flex items-center gap-2 text-sm text-muted transition-colors hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" aria-hidden />
        Back to RAMS list
      </Link>

      <h1 className="text-2xl font-bold tracking-tight">Create New RAMS</h1>
      <p className="mt-1 text-sm text-muted">
        Fill in the project details once — a draft is saved before AI generation.
      </p>

      {/* Stepper */}
      <ol className="mt-6 flex items-center" aria-label="Progress">
        {STEPS.map((label, i) => (
          <li key={label} className="flex flex-1 items-center last:flex-none">
            <div className="flex items-center gap-2">
              <span
                className={cn(
                  "flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold",
                  i < step && "bg-success text-white",
                  i === step && "bg-accent text-accent-foreground",
                  i > step && "bg-surface-muted text-muted"
                )}
                aria-current={i === step ? "step" : undefined}
              >
                {i < step ? <Check className="h-4 w-4" aria-hidden /> : i + 1}
              </span>
              <span
                className={cn(
                  "hidden text-sm font-medium sm:block",
                  i === step ? "text-foreground" : "text-muted"
                )}
              >
                {label}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <div className={cn("mx-3 h-px flex-1", i < step ? "bg-success" : "bg-border")} aria-hidden />
            )}
          </li>
        ))}
      </ol>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>
            Step {step + 1} — {STEPS[step]}
          </CardTitle>
          <CardDescription>
            {step === 3
              ? "Review everything before creating the draft."
              : "Fields marked * are required."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {step < 3 ? (
            <div className="grid gap-4">
              {STEP_FIELDS[step].map((key) => (
                <Field
                  key={key}
                  id={key}
                  label={LABELS[key]}
                  required={key === "project_name" || key === "work_description"}
                  multiline={MULTILINE.includes(key)}
                  value={input[key]}
                  onChange={(e) => set(key, e.target.value)}
                  error={errors[key]}
                  placeholder={key === "project_name" ? "Riverside Warehouse Fit-Out" : undefined}
                />
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {companyName && (
                <Alert variant="info" title="Company details attached">
                  {companyName} — saved in your profile, automatically included
                  in the generated document.
                </Alert>
              )}
              {([0, 1, 2] as const).map((s) => (
                <div key={s} className="rounded-lg border border-border">
                  <div className="border-b border-border bg-surface-muted px-4 py-2 text-sm font-semibold">
                    {STEPS[s]}
                  </div>
                  <dl className="space-y-2 px-4 py-3">
                    {STEP_FIELDS[s].map((key) => (
                      <div key={key} className="grid gap-1 sm:grid-cols-3">
                        <dt className="text-xs font-medium uppercase tracking-wide text-muted">
                          {LABELS[key]}
                        </dt>
                        <dd className="whitespace-pre-wrap text-sm sm:col-span-2">
                          {input[key] || <span className="text-muted">—</span>}
                        </dd>
                      </div>
                    ))}
                  </dl>
                </div>
              ))}
              <Button
                variant="accent"
                size="lg"
                className="w-full"
                onClick={onCreate}
                loading={creating}
                disabled={creating}
              >
                <ClipboardCheck className="h-5 w-5" aria-hidden />
                Create RAMS Draft
              </Button>
            </div>
          )}

          {step < 3 && (
            <div className="mt-6 flex justify-between border-t border-border pt-4">
              <Button
                variant="outline"
                onClick={() => setStep((s) => Math.max(s - 1, 0))}
                disabled={step === 0}
              >
                <ArrowLeft className="h-4 w-4" aria-hidden />
                Back
              </Button>
              <Button variant="primary" onClick={next}>
                Continue
                <ArrowRight className="h-4 w-4" aria-hidden />
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
