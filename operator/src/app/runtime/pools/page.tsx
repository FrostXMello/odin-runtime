"use client";

import { useQuery } from "@tanstack/react-query";
import { runtimeApi } from "@/lib/api/runtime";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { MetricTile } from "@/components/ui/metric-tile";

export default function RuntimePoolsPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "pools"],
    queryFn: () => runtimeApi.pools(),
    refetchInterval: 3000,
  });

  const pools = data?.pools ?? {};

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">
        Execution pools · default {data?.default ?? "local"}
      </h2>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {Object.entries(pools).map(([name, m]) => (
          <Card key={name}>
            <CardHeader title={name} subtitle="pool pressure" />
            <CardBody className="grid grid-cols-2 gap-2">
              <MetricTile label="Active" value={m.active ?? 0} />
              <MetricTile label="Max" value={m.max_concurrent ?? 0} />
              <MetricTile label="Completed" value={m.completed ?? 0} />
              <MetricTile label="Rejected" value={m.rejected ?? 0} />
            </CardBody>
          </Card>
        ))}
      </div>
    </div>
  );
}
