import type { Metadata } from "next";
import { ComingSoon } from "@/components/coming-soon";

export const metadata: Metadata = { title: "Privacy Policy" };

export default function PrivacyPage() {
  return <ComingSoon title="Privacy Policy" />;
}
