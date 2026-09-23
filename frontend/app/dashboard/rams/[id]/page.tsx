"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Sparkles } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { getRams, type Rams } from "@/lib/rams";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/badge";
import { Alert } from "@/components/ui/alert";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";
import { useToast } from "@/components/ui/toast";

const GENERATE_STAGES = [
  "Preparing...",
  "Generating AI content...",
  "Validating structured output...",
  "Saving draft...",
  "Complete",
];

interface GeneratedHazard {
  hazard: string;
  who_might_be_harmed: string;
  existing_controls: string;
  initial_likelihood: number;
  initial_severity: number;
  initial_risk_score: number;
  additional_controls: string;
  residual_likelihood: number;
  residual_severity: number;
  residual_risk_score: number;
}

export default function RamsDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { toast } = useToast();
  const [rams, setRams] = useState<Rams | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [stage, setStage] = useState(0);
  const [canGenerate, setCanGenerate] = useState<boolean | null>(null);
  const [genError, setGenError] = useState<string | null>(null);

  useEffect(() => {
    getRams(id)
      .then(setRams)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
    apiFetch<{ can_generate: boolean }>("/api/subscription")
      .then((s) => setCanGenerate(s.can_generate))
      .catch(() => setCanGenerate(false));
  }, [id]);

  async function onGenerate() {
    if (generating) return; // duplicate guard
    setGenerating(true);
    setGenError(null);
    setStage(0);

    // Staged progress animation (mock generation is fast; real AI takes longer)
    const timer = setInterval(() => {
      setStage((s) => Math.min(s + 1, GENERATE_STAGES.length - 2));
    }, 600);

    try {
      const res = await apiFetch<{ status: string; generated_hazards: number }>(
        `/api/rams/${id}/generate`,
        { method: "POST" }
      );
      clearInterval(timer);
      setStage(GENERATE_STAGES.length - 1);
      const updated = await getRams(id);
      setRams(updated);
      toast({
        title: "AI content generated",
        description: `${res.generated_hazards} hazards drafted. Document production arrives in the next phase.`,
        variant: "success",
      });
    } catch (e) {
      clearInterval(timer);
      const message = e instanceof Error ? e.message : "Generation failed.";
      setGenError(message);
      const updated = await getRams(id).catch(() => null);
      if (updated) setRams(updated);
      toast({ title: "Generation failed", description: message, variant: "danger" });
    } finally {
      setGenerating(false);
    }
  }

  if (loading) return <LoadingState label="Loading RAMS..." />;
  if (error || !rams)
    return (
      <ErrorState
        title="RAMS not found"
        message={error ?? "This document may have been deleted."}
        onRetry={() => window.location.reload()}
      />
    );

  const entries = Object.entries(rams.input_data ?? {}).filter(
    ([, v]) => typeof v === "string" && v.trim()
  );
  const hazards: GeneratedHazard[] =
    (rams.generated_data?.hazards as GeneratedHazard[] | undefined) ?? [];
  const method = rams.generated_data?.method_statement as
    | { preparation: string; execution: string; completion: string }
    | undefined;

  return (
    <div className="mx-auto max-w-3xl">
      <Link
        href="/dashboard/rams"
        className="mb-6 inline-flex items-center gap-2 text-sm text-muted transition-colors hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" aria-hidden />
        Back to RAMS list
      </Link>

      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{rams.project_name}</h1>
          <p className="mt-1 text-sm text-muted">
            {rams.document_number ?? "—"}
            {rams.client_name ? ` · ${rams.client_name}` : ""}
          </p>
        </div>
        <StatusBadge status={rams.status} />
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Submitted information</CardTitle>
          <CardDescription>Exactly what was entered in the wizard.</CardDescription>
        </CardHeader>
        <CardContent>
          {entries.length === 0 ? (
            <p className="text-sm text-muted">No details recorded.</p>
          ) : (
            <dl className="space-y-3">
              {entries.map(([key, value]) => (
                <div key={key} className="grid gap-1 sm:grid-cols-3">
                  <dt className="text-xs font-medium uppercase tracking-wide text-muted">
                    {key.replace(/_/g, " ")}
                  </dt>
                  <dd className="whitespace-pre-wrap text-sm sm:col-span-2">
                    {String(value)}
                  </dd>
                </div>
              ))}
            </dl>
          )}
        </CardContent>
      </Card>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>AI generation</CardTitle>
          <CardDescription>
            Structured hazards, method statement and controls.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {canGenerate === false && rams.status === "draft" && (
            <Alert variant="warning" title="Subscription required">
              An active subscription is required to generate a RAMS.{" "}
              <Link href="/dashboard/settings/billing" className="font-medium underline underline-offset-4">
                Go to billing
              </Link>
            </Alert>
          )}

          {genError && (
            <Alert variant="danger" title="Generation failed" className="mb-4">
              {genError}
            </Alert>
          )}

          {rams.status === "draft" || rams.status === "failed" ? (
            <>
              {rams.status === "failed" && rams.generation_error && !genError && (
                <Alert variant="danger" title="Last attempt failed" className="mb-4">
                  {rams.generation_error}
                </Alert>
              )}
              {generating ? (
                <div aria-live="polite" className="flex items-center gap-3 rounded-lg bg-surface-muted p-4">
                  <span className="h-5 w-5 animate-spin rounded-full border-2 border-border border-t-accent" aria-hidden />
                  <p className="text-sm font-medium">{GENERATE_STAGES[stage]}</p>
                </div>
              ) : (
                <Button
                  variant="accent"
                  size="lg"
                  className="w-full"
                  onClick={onGenerate}
                  disabled={canGenerate === false}
                >
                  <Sparkles className="h-5 w-5" aria-hidden />
                  Generate RAMS with AI
                </Button>
              )}
            </>
          ) : null}

          {hazards.length > 0 && (
            <div className="mt-6">
              <h3 className="font-semibold">Risk assessment ({hazards.length} hazards)</h3>
              <div className="mt-3 space-y-3">
                {hazards.map((h, i) => (
                  <div key={i} className="rounded-lg border border-border p-4">
                    <p className="font-medium">{h.hazard}</p>
                    <div className="mt-2 grid gap-2 text-sm sm:grid-cols-2">
                      <p>
                        <span className="text-muted">Who: </span>
                        {h.who_might_be_harmed}
                      </p>
                      <p>
                        <span className="text-muted">Initial risk: </span>
                        {h.initial_likelihood} × {h.initial_severity} ={" "}
                        <strong>{h.initial_risk_score}</strong>
                      </p>
                      <p className="sm:col-span-2">
                        <span className="text-muted">Existing controls: </span>
                        {h.existing_controls}
                      </p>
                      <p className="sm:col-span-2">
                        <span className="text-muted">Additional controls: </span>
                        {h.additional_controls}
                      </p>
                      <p>
                        <span className="text-muted">Residual risk: </span>
                        {h.residual_likelihood} × {h.residual_severity} ={" "}
                        <strong>{h.residual_risk_score}</strong>
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              {method && (
                <div className="mt-6">
                  <h3 className="font-semibold">Method statement</h3>
                  <div className="mt-3 space-y-3 text-sm">
                    <div className="rounded-lg border border-border p-4">
                      <p className="font-medium">Preparation</p>
                      <p className="mt-1 text-muted">{method.preparation}</p>
                    </div>
                    <div className="rounded-lg border border-border p-4">
                      <p className="font-medium">Execution</p>
                      <p className="mt-1 text-muted">{method.execution}</p>
                    </div>
                    <div className="rounded-lg border border-border p-4">
                      <p className="font-medium">Completion</p>
                      <p className="mt-1 text-muted">{method.completion}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
