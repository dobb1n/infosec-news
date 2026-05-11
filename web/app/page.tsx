import { listDigests } from "@/lib/gcs";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  let digests: Awaited<ReturnType<typeof listDigests>> = [];
  let error: string | null = null;

  try {
    digests = await listDigests();
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed to load digests";
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Reports</h1>
      {error && (
        <p className="text-red-400 text-sm bg-red-950 border border-red-800 rounded px-4 py-3">
          {error}
        </p>
      )}
      {!error && digests.length === 0 && (
        <p className="text-gray-500">No reports yet.</p>
      )}
      <ul className="space-y-2">
        {digests.map((d) => (
          <li key={d.slug}>
            <Link
              href={`/report/${d.slug}`}
              className="flex items-center justify-between px-4 py-3 bg-gray-900 border border-gray-800 rounded-lg hover:border-gray-600 hover:bg-gray-800 transition-colors group"
            >
              <span className="font-medium group-hover:text-white">{d.date}</span>
              <span className="text-gray-500 text-sm">View stories →</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
