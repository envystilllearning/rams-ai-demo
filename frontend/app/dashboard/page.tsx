import { createClient } from "@/lib/supabase/server";
import { Card, CardContent, CardDescription, CardTitle } from "@/components/ui/card";

export default async function DashboardPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  const name =
    user?.user_metadata?.full_name?.split(" ")[0] || user?.email || "there";

  return (
    <div>
      <h1 className="text-2xl font-bold tracking-tight">Welcome back, {name}</h1>
      <p className="mt-1 text-sm text-muted">
        Your dashboard is under construction — full features arriving in the
        next phase.
      </p>
      <Card className="mt-8">
        <CardContent>
          <CardTitle>Session verified</CardTitle>
          <CardDescription>
            You are authenticated as {user?.email}. Subscription, RAMS creation
            and document downloads will appear here.
          </CardDescription>
        </CardContent>
      </Card>
    </div>
  );
}
