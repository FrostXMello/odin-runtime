import { redirect } from "next/navigation";

export default async function MissionDetailRedirect({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  redirect(`/missions?mission=${id}`);
}
