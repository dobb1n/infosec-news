import { NextResponse } from "next/server";
import { generateEscalationReport, escalationFilename } from "@/lib/escalate";
import { saveEscalation } from "@/lib/gcs";

export async function POST(req: Request) {
  let body: { title?: string; url?: string; published?: string; summary?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const { title, url, published, summary } = body;
  if (!title || !url) {
    return NextResponse.json({ error: "title and url are required" }, { status: 400 });
  }

  try {
    const report = await generateEscalationReport(
      title,
      url,
      published ?? "",
      summary ?? ""
    );

    const slug = escalationFilename(title);

    try {
      await saveEscalation(slug, report);
    } catch {
      // GCS save is best-effort; still return the report to the client
    }

    return NextResponse.json({ report, slug });
  } catch (e) {
    const message = e instanceof Error ? e.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
