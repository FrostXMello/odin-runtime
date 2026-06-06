"use client";

import { useMissions } from "@/lib/hooks/use-runtime-health";
import { MissionCreateForm } from "@/components/missions/mission-create-form";
import { MissionRow } from "@/components/missions/mission-row";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function MissionsPage() {
  const { data, isLoading, isError } = useMissions();

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h2 className="text-lg font-medium text-slate-100">Mission workbench</h2>
        <p className="mt-1 text-sm text-odin-muted">
          Every action starts here. Create a mission, watch it run, recover if interrupted.
        </p>
      </div>
      <MissionCreateForm />
      <Card>
        <CardHeader
          title="Your missions"
          subtitle={isLoading ? "Loading…" : `${data?.length ?? 0} in store`}
        />
        <CardBody>
          {isError && (
            <p className="text-sm text-rose-400">Could not load missions — is the backend running?</p>
          )}
          <div className="space-y-2">
            {(data ?? []).map((m) => (
              <MissionRow key={m.mission_id} mission={m} />
            ))}
            {!isLoading && !isError && !data?.length && (
              <p className="py-8 text-center text-sm text-odin-muted">
                No missions yet — describe your first goal above.
              </p>
            )}
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
