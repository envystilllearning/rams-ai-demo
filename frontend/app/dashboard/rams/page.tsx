"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Download, FilePlus2, FileText, Trash2 } from "lucide-react";
import { deleteRams, listRams, type Rams } from "@/lib/rams";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { Modal } from "@/components/ui/modal";
import { useToast } from "@/components/ui/toast";

function formatDate(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function RamsListPage() {
  const { toast } = useToast();
  const [items, setItems] = useState<Rams[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Rams | null>(null);
  const [deleting, setDeleting] = useState(false);

  async function load() {
    setLoading(true);
    try {
      setError(null);
      const res = await listRams();
      setItems(res.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function onDelete() {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await deleteRams(deleteTarget.id);
      setItems((prev) => prev.filter((r) => r.id !== deleteTarget.id));
      toast({ title: "RAMS deleted", variant: "info" });
    } catch (e) {
      toast({
        title: "Delete failed",
        description: e instanceof Error ? e.message : "Please try again.",
        variant: "danger",
      });
    } finally {
      setDeleting(false);
      setDeleteTarget(null);
    }
  }

  if (loading) return <LoadingState label="Loading RAMS..." />;
  if (error)
    return <ErrorState title="Failed to load RAMS" message={error} onRetry={load} />;

  return (
    <div>
      <Link
        href="/dashboard"
        className="mb-6 inline-flex items-center gap-2 text-sm text-muted transition-colors hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" aria-hidden />
        Back to dashboard
      </Link>

      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Your RAMS</h1>
          <p className="mt-1 text-sm text-muted">
            {items.length === 0
              ? "No documents yet — create your first one."
              : `${items.length} document${items.length === 1 ? "" : "s"}`}
          </p>
        </div>
        <Link
          href="/dashboard/rams/new"
          className="inline-flex h-10 items-center gap-2 rounded-lg bg-accent px-4 text-sm font-semibold text-accent-foreground shadow-sm transition-colors hover:bg-accent-hover"
        >
          <FilePlus2 className="h-4 w-4" aria-hidden />
          Create New RAMS
        </Link>
      </div>

      {items.length === 0 ? (
        <div className="mt-8">
          <EmptyState
            icon={<FileText className="h-8 w-8" aria-hidden />}
            title="No RAMS yet"
            description="Enter your project details once and get a professional draft document."
            action={
              <Link
                href="/dashboard/rams/new"
                className="inline-flex h-10 items-center gap-2 rounded-lg bg-accent px-4 text-sm font-semibold text-accent-foreground shadow-sm transition-colors hover:bg-accent-hover"
              >
                <FilePlus2 className="h-4 w-4" aria-hidden />
                Create your first RAMS
              </Link>
            }
          />
        </div>
      ) : (
        <div className="mt-6 overflow-hidden rounded-xl border border-border bg-surface">
          <ul className="divide-y divide-border">
            {items.map((r) => (
              <li
                key={r.id}
                className="flex items-center justify-between gap-4 px-5 py-4 transition-colors hover:bg-surface-muted/50"
              >
                <div className="min-w-0">
                  <Link
                    href={`/dashboard/rams/${r.id}`}
                    className="truncate font-medium text-foreground underline-offset-4 hover:underline"
                  >
                    {r.project_name}
                  </Link>
                  <p className="mt-0.5 text-xs text-muted">
                    {r.document_number ?? "—"} · {formatDate(r.created_at)}
                    {r.client_name ? ` · ${r.client_name}` : ""}
                  </p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  <StatusBadge status={r.status} />
                  {r.status === "ready" ? (
                    <span className="text-muted" title="Downloads arrive with the document phase">
                      <Download className="h-4 w-4" aria-hidden />
                    </span>
                  ) : null}
                  <button
                    onClick={() => setDeleteTarget(r)}
                    aria-label={`Delete ${r.project_name}`}
                    className="rounded-lg p-1.5 text-muted transition-colors hover:bg-danger-soft hover:text-danger"
                  >
                    <Trash2 className="h-4 w-4" aria-hidden />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <Modal
        open={deleteTarget !== null}
        onClose={() => setDeleteTarget(null)}
        title="Delete RAMS?"
      >
        <p className="text-sm text-muted">
          Permanently delete{" "}
          <strong className="text-foreground">{deleteTarget?.project_name}</strong>?
          This cannot be undone.
        </p>
        <div className="mt-5 flex justify-end gap-3">
          <Button variant="outline" onClick={() => setDeleteTarget(null)}>
            Keep
          </Button>
          <Button variant="danger" onClick={onDelete} loading={deleting}>
            Delete
          </Button>
        </div>
      </Modal>
    </div>
  );
}
