"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { ArrowLeft, CreditCard, ExternalLink } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/badge";
import { Alert } from "@/components/ui/alert";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";
import { Modal } from "@/components/ui/modal";
import { useToast } from "@/components/ui/toast";

interface Subscription {
  status: string;
  can_generate: boolean;
  price_label: string;
  cancel_at_period_end: boolean;
  current_period_end: string | null;
  provider: string;
}

export default function BillingPage() {
  const { toast } = useToast();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [sub, setSub] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [confirmCancel, setConfirmCancel] = useState(false);

  const load = useCallback(async () => {
    try {
      setError(null);
      const data = await apiFetch<Subscription>("/api/subscription");
      setSub(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    // Success/cancel return markers from Stripe redirect flow
    if (searchParams.get("success")) {
      toast({ title: "Subscription activated", variant: "success" });
    }
    if (searchParams.get("canceled")) {
      toast({ title: "Checkout canceled", variant: "info" });
    }
  }, [load, searchParams, toast]);

  async function onSubscribe() {
    setActionLoading("checkout");
    try {
      const res = await apiFetch<{
        status: string;
        url: string | null;
        message: string | null;
      }>("/api/stripe/checkout", { method: "POST" });

      if (res.url) {
        window.location.href = res.url; // real Stripe redirect
        return;
      }
      toast({
        title: "Subscription active",
        description: res.message ?? "You can now generate RAMS.",
        variant: "success",
      });
      await load();
    } catch (e) {
      toast({
        title: "Checkout failed",
        description: e instanceof Error ? e.message : "Please try again.",
        variant: "danger",
      });
    } finally {
      setActionLoading(null);
    }
  }

  async function onPortal() {
    setActionLoading("portal");
    try {
      const res = await apiFetch<{
        status: string;
        url: string | null;
        message: string | null;
      }>("/api/stripe/portal", { method: "POST" });
      if (res.url) {
        window.location.href = res.url;
        return;
      }
      toast({ title: "Customer portal", description: res.message ?? undefined, variant: "info" });
    } catch (e) {
      toast({
        title: "Portal failed",
        description: e instanceof Error ? e.message : "Please try again.",
        variant: "danger",
      });
    } finally {
      setActionLoading(null);
    }
  }

  async function onCancel() {
    setConfirmCancel(false);
    setActionLoading("cancel");
    try {
      await apiFetch<{ status: string }>("/api/billing/cancel", { method: "POST" });
      toast({
        title: "Subscription canceled",
        description: "Generation access has been removed.",
        variant: "info",
      });
      await load();
    } catch (e) {
      toast({
        title: "Cancel failed",
        description: e instanceof Error ? e.message : "Please try again.",
        variant: "danger",
      });
    } finally {
      setActionLoading(null);
    }
  }

  if (loading) return <LoadingState label="Loading billing..." />;
  if (error)
    return <ErrorState title="Failed to load billing" message={error} onRetry={load} />;

  const isActive = sub?.can_generate ?? false;
  const isMock = sub?.provider === "mock";

  return (
    <div className="mx-auto max-w-2xl">
      <Link
        href="/dashboard"
        className="mb-6 inline-flex items-center gap-2 text-sm text-muted transition-colors hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" aria-hidden />
        Back to dashboard
      </Link>

      <h1 className="text-2xl font-bold tracking-tight">Billing</h1>
      <p className="mt-1 text-sm text-muted">
        Manage your subscription. Generation requires an active plan.
      </p>

      {searchParams.get("canceled") && (
        <Alert variant="warning" title="Checkout canceled" className="mt-4">
          No charges were made. You can subscribe again any time.
        </Alert>
      )}

      <Card className="mt-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Subscription</CardTitle>
              <CardDescription>Professional plan · {sub?.price_label}</CardDescription>
            </div>
            <StatusBadge status={sub?.status === "none" ? "canceled" : (sub?.status ?? "canceled")} />
          </div>
        </CardHeader>
        <CardContent>
          {isActive ? (
            <Alert variant="success" title="Subscription active">
              You can create and generate RAMS{sub?.cancel_at_period_end ? " until the end of the current period" : ""}.
            </Alert>
          ) : (
            <Alert variant="warning" title="No active subscription">
              An active subscription is required to generate a RAMS.
            </Alert>
          )}

          {isMock && (
            <p className="mt-4 text-xs text-muted">
              Demo mode: payments are simulated — no Stripe account or card is
              involved. Switching to live Stripe later requires zero code
              changes (set PAYMENT_PROVIDER=stripe).
            </p>
          )}

          <div className="mt-6 flex flex-wrap gap-3">
            {!isActive && (
              <Button
                variant="accent"
                onClick={onSubscribe}
                loading={actionLoading === "checkout"}
                disabled={actionLoading !== null}
              >
                <CreditCard className="h-4 w-4" aria-hidden />
                Start Subscription — {sub?.price_label}
              </Button>
            )}
            {isActive && (
              <>
                <Button variant="outline" onClick={onPortal} loading={actionLoading === "portal"} disabled={actionLoading !== null}>
                  <ExternalLink className="h-4 w-4" aria-hidden />
                  Manage Subscription
                </Button>
                {!isMock && sub?.cancel_at_period_end === false && (
                  <Button variant="ghost" onClick={() => setConfirmCancel(true)} disabled={actionLoading !== null}>
                    Cancel subscription
                  </Button>
                )}
                {isMock && (
                  <Button variant="ghost" onClick={() => setConfirmCancel(true)} disabled={actionLoading !== null}>
                    Cancel subscription
                  </Button>
                )}
              </>
            )}
          </div>
        </CardContent>
      </Card>

      <Modal open={confirmCancel} onClose={() => setConfirmCancel(false)} title="Cancel subscription?">
        <p className="text-sm text-muted">
          Your subscription will be {isMock ? "canceled immediately and access removed" : "canceled at the end of the current period"}. Are you sure?
        </p>
        <div className="mt-5 flex justify-end gap-3">
          <Button variant="outline" onClick={() => setConfirmCancel(false)}>
            Keep subscription
          </Button>
          <Button variant="danger" onClick={onCancel} loading={actionLoading === "cancel"}>
            Cancel subscription
          </Button>
        </div>
      </Modal>
    </div>
  );
}
