import type { Metadata } from "next";
import { ComingSoon } from "@/components/coming-soon";

export const metadata: Metadata = { title: "Terms of Service" };

export default function TermsPage() {
  return <ComingSoon title="Terms of Service" />;
}
