"use client";

import { useState } from "react";
import { FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge, StatusBadge } from "@/components/ui/badge";
import { Alert } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { LoadingState } from "@/components/ui/loading-state";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { Modal } from "@/components/ui/modal";
import { SectionHeading } from "@/components/ui/section-heading";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { ToastProvider, useToast } from "@/components/ui/toast";

function PreviewContent() {
  const { toast } = useToast();
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <main className="mx-auto max-w-5xl px-6 py-12">
      {/* Header */}
      <header className="mb-12 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <FileText className="h-5 w-5" aria-hidden />
          </div>
          <div>
            <p className="font-bold text-foreground">RAMS AI</p>
            <p className="text-xs text-muted">Design System Preview</p>
          </div>
        </div>
        <ThemeToggle />
      </header>

      <Alert variant="info" title="Temporary page">
        This preview will be replaced by the real landing page in Phase 5.
        Use the moon/sun toggle to check dark mode.
      </Alert>

      {/* Buttons */}
      <section className="mt-12">
        <SectionHeading
          align="left"
          eyebrow="Actions"
          title="Buttons"
        />
        <Card>
          <CardContent className="flex flex-wrap items-center gap-3">
            <Button>Primary</Button>
            <Button variant="accent">Start Creating RAMS</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="danger">Danger</Button>
            <Button loading>Loading</Button>
            <Button disabled>Disabled</Button>
          </CardContent>
        </Card>
      </section>

      {/* Forms */}
      <section className="mt-12">
        <SectionHeading align="left" eyebrow="Forms" title="Inputs" />
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="demo-project" className="mb-1.5 block text-sm font-medium">
              Project name
            </label>
            <Input id="demo-project" placeholder="Riverside Warehouse Fit-Out" />
          </div>
          <div>
            <label htmlFor="demo-client" className="mb-1.5 block text-sm font-medium">
              Client (with error)
            </label>
            <Input id="demo-client" defaultValue="" error="Client name is required" />
          </div>
          <div>
            <label htmlFor="demo-risk" className="mb-1.5 block text-sm font-medium">
              Risk level
            </label>
            <Select id="demo-risk" defaultValue="medium">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </Select>
          </div>
          <div className="sm:col-span-2">
            <label htmlFor="demo-notes" className="mb-1.5 block text-sm font-medium">
              Site restrictions
            </label>
            <Textarea
              id="demo-notes"
              placeholder="Describe any site restrictions..."
            />
          </div>
        </div>
      </section>

      {/* Cards + Badges */}
      <section className="mt-12">
        <SectionHeading align="left" eyebrow="Data" title="Cards & status badges" />
        <div className="grid gap-6 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Subscription</CardTitle>
              <CardDescription>Your plan and billing</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">
                £9.95<span className="text-sm font-normal text-muted">/month</span>
              </p>
              <div className="mt-2">
                <StatusBadge status="active" />
              </div>
            </CardContent>
            <CardFooter>
              <Button variant="outline" size="sm">Manage →</Button>
            </CardFooter>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Subscription states</CardTitle>
              <CardDescription>All Stripe states (PRD §4)</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {["active", "trialing", "past_due", "canceled", "unpaid", "incomplete"].map(
                (s) => (
                  <StatusBadge key={s} status={s} />
                )
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>RAMS statuses</CardTitle>
              <CardDescription>Document lifecycle</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {["draft", "generating", "ready", "failed"].map((s) => (
                <StatusBadge key={s} status={s} />
              ))}
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Alerts */}
      <section className="mt-12">
        <SectionHeading align="left" eyebrow="Feedback" title="Alerts" />
        <div className="grid gap-3">
          <Alert variant="success" title="RAMS ready">
            Your document has been generated and is ready to download.
          </Alert>
          <Alert variant="danger" title="Generation failed">
            We couldn&apos;t generate your RAMS right now. No document has been
            created. Please try again.
          </Alert>
          <Alert variant="warning" title="Subscription required">
            An active subscription is required to generate a RAMS.
          </Alert>
        </div>
      </section>

      {/* States */}
      <section className="mt-12">
        <SectionHeading align="left" eyebrow="UI states" title="Loading, empty, error" />
        <div className="grid gap-6 lg:grid-cols-3">
          <Card>
            <CardContent className="p-0">
              <LoadingState label="Generating RAMS..." />
              <div className="space-y-2 p-6 pt-0">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent>
              <EmptyState
                icon={<FileText className="h-8 w-8" aria-hidden />}
                title="No RAMS yet"
                description="Create your first RAMS to see it here."
              />
            </CardContent>
          </Card>
          <Card>
            <CardContent>
              <ErrorState
                title="Failed to load RAMS"
                message="Could not reach the server. Please try again."
                onRetry={() => toast({ title: "Retrying...", variant: "info" })}
              />
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Toast + Modal demos */}
      <section className="mt-12 mb-8">
        <SectionHeading align="left" eyebrow="Overlays" title="Toast & modal" />
        <Card>
          <CardContent className="flex flex-wrap gap-3">
            <Button
              variant="outline"
              onClick={() =>
                toast({ title: "RAMS ready", description: "Download DOCX or PDF.", variant: "success" })
              }
            >
              Success toast
            </Button>
            <Button
              variant="outline"
              onClick={() =>
                toast({ title: "Generation failed", description: "No document created.", variant: "danger" })
              }
            >
              Error toast
            </Button>
            <Button onClick={() => setModalOpen(true)}>Open modal</Button>
          </CardContent>
        </Card>
      </section>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Confirm generation">
        <p className="text-sm text-muted">
          Generate RAMS for <strong className="text-foreground">Riverside Warehouse Fit-Out</strong>?
          This uses one AI generation credit.
        </p>
        <div className="mt-5 flex justify-end gap-3">
          <Button variant="outline" onClick={() => setModalOpen(false)}>
            Cancel
          </Button>
          <Button
            variant="accent"
            onClick={() => {
              setModalOpen(false);
              toast({ title: "Generating...", description: "AI drafting your RAMS.", variant: "info" });
            }}
          >
            Generate RAMS
          </Button>
        </div>
      </Modal>

      {/* Badge samples */}
      <section className="mb-16">
        <SectionHeading align="left" eyebrow="Misc" title="Badges" />
        <div className="flex flex-wrap gap-2">
          <Badge variant="neutral">Neutral</Badge>
          <Badge variant="info">Info</Badge>
          <Badge variant="success">Success</Badge>
          <Badge variant="warning">Warning</Badge>
          <Badge variant="danger">Danger</Badge>
          <Badge variant="accent">£9.95/month</Badge>
        </div>
      </section>
    </main>
  );
}

export default function PreviewPage() {
  return (
    <ToastProvider>
      <PreviewContent />
    </ToastProvider>
  );
}
