"use client";

import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ActionValidationPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Action validation</h2>
      <Card>
        <CardHeader title="Verification layer" subtitle="Simulation / supervised / semi-autonomous" />
        <CardBody className="text-xs text-slate-400">
          OCR validation, click confidence, and post-action state checks. Destructive actions remain blocked.
        </CardBody>
      </Card>
    </div>
  );
}
