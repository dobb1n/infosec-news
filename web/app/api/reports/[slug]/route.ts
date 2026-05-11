import { NextResponse } from "next/server";
import { getDigest } from "@/lib/gcs";
import { parseStories } from "@/lib/parser";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params;
  try {
    const content = await getDigest(slug);
    const stories = parseStories(content);
    return NextResponse.json({ slug, stories });
  } catch (e) {
    const message = e instanceof Error ? e.message : "Unknown error";
    const status = message.includes("No such object") ? 404 : 500;
    return NextResponse.json({ error: message }, { status });
  }
}
