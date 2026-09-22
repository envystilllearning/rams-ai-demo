"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { apiFetch, type Profile } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert } from "@/components/ui/alert";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { useToast } from "@/components/ui/toast";

export default function CompanySettingsPage() {
  const { toast } = useToast();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    apiFetch<Profile>("/api/profile")
      .then(setProfile)
      .catch((e: Error) => setLoadError(e.message))
      .finally(() => setLoading(false));
  }, []);

  function setField(key: keyof Profile, value: string) {
    setProfile((p) => (p ? { ...p, [key]: value } : p));
    setFieldErrors((f) => ({ ...f, [key]: "" }));
  }

  function validate(): boolean {
    const errors: Record<string, string> = {};
    if (!profile?.company_name?.trim()) {
      errors.company_name = "Company name is required";
    }
    if (profile?.company_postcode && profile.company_postcode.trim().length > 20) {
      errors.company_postcode = "Postcode is too long";
    }
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function onSave() {
    if (!validate() || !profile) return;
    setSaving(true);
    try {
      const updated = await apiFetch<Profile>("/api/profile", {
        method: "PATCH",
        body: JSON.stringify({
          full_name: profile.full_name,
          company_name: profile.company_name,
          company_address: profile.company_address,
          company_postcode: profile.company_postcode,
          company_phone: profile.company_phone,
        }),
      });
      setProfile(updated);
      toast({
        title: "Profile saved",
        description: "Company details will be reused in every RAMS you create.",
        variant: "success",
      });
    } catch (e) {
      toast({
        title: "Save failed",
        description: e instanceof Error ? e.message : "Please try again.",
        variant: "danger",
      });
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <LoadingState label="Loading company profile..." />;
  }

  if (loadError) {
    return (
      <ErrorState
        title="Failed to load profile"
        message={loadError}
        onRetry={() => window.location.reload()}
      />
    );
  }

  return (
    <div className="mx-auto max-w-2xl">
      <Link
        href="/dashboard"
        className="mb-6 inline-flex items-center gap-2 text-sm text-muted transition-colors hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" aria-hidden />
        Back to dashboard
      </Link>

      <h1 className="text-2xl font-bold tracking-tight">Company Profile</h1>
      <p className="mt-1 text-sm text-muted">
        Saved once, reused automatically in every RAMS you generate.
      </p>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Company information</CardTitle>
          <CardDescription>
            Appears on generated documents as the responsible company.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label htmlFor="full_name" className="mb-1.5 block text-sm font-medium">
                Your full name
              </label>
              <Input
                id="full_name"
                value={profile?.full_name ?? ""}
                onChange={(e) => setField("full_name", e.target.value)}
                placeholder="John Smith"
              />
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="company_name" className="mb-1.5 block text-sm font-medium">
                Company name <span className="text-danger">*</span>
              </label>
              <Input
                id="company_name"
                value={profile?.company_name ?? ""}
                onChange={(e) => setField("company_name", e.target.value)}
                error={fieldErrors.company_name}
                placeholder="Northbridge Construction Ltd"
              />
              {fieldErrors.company_name && (
                <p id="company_name-error" className="mt-1 text-xs text-danger">
                  {fieldErrors.company_name}
                </p>
              )}
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="company_address" className="mb-1.5 block text-sm font-medium">
                Company address
              </label>
              <Input
                id="company_address"
                value={profile?.company_address ?? ""}
                onChange={(e) => setField("company_address", e.target.value)}
                placeholder="25 Industrial Park"
              />
            </div>

            <div>
              <label htmlFor="company_postcode" className="mb-1.5 block text-sm font-medium">
                Postcode
              </label>
              <Input
                id="company_postcode"
                value={profile?.company_postcode ?? ""}
                onChange={(e) => setField("company_postcode", e.target.value)}
                error={fieldErrors.company_postcode}
                placeholder="M1 1AA"
              />
            </div>

            <div>
              <label htmlFor="company_phone" className="mb-1.5 block text-sm font-medium">
                Phone
              </label>
              <Input
                id="company_phone"
                type="tel"
                value={profile?.company_phone ?? ""}
                onChange={(e) => setField("company_phone", e.target.value)}
                placeholder="0161 000 0000"
              />
            </div>
          </div>

          <Alert variant="info" title="Email & logo">
            Email comes from your account and cannot be changed here. Logo
            upload arrives with the storage phase.
          </Alert>

          <div className="flex justify-end gap-3 border-t border-border pt-4">
            <Button variant="accent" onClick={onSave} loading={saving} disabled={saving}>
              Save Changes
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
