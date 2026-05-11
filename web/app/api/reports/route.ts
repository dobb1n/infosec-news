import { NextResponse } from "next/server";
import { listDigests } from "@/lib/gcs";

export async function GET() {
  try {
    const digests = await listDigests();
    return NextResponse.json(digests);
  } catch (e) {
    const message = e instanceof Error ? e.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
