import { getDigest } from "@/lib/gcs";
import { parseStories } from "@/lib/parser";
import { notFound } from "next/navigation";
import Link from "next/link";
import StoryCard from "@/components/StoryCard";

export const dynamic = "force-dynamic";

interface Props {
  params: Promise<{ slug: string }>;
}

export default async function ReportPage({ params }: Props) {
  const { slug } = await params;

  let content: string;
  try {
    content = await getDigest(slug);
  } catch {
    notFound();
  }

  const stories = parseStories(content);

  const date = (() => {
    const match = slug.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (!match) return slug;
    return new Date(`${slug}T00:00:00Z`).toLocaleDateString("en-GB", {
      year: "numeric",
      month: "long",
      day: "numeric",
      timeZone: "UTC",
    });
  })();

  return (
    <div>
      <div className="mb-6">
        <Link href="/" className="text-sm text-gray-500 hover:text-gray-300 transition-colors">
          ← All reports
        </Link>
        <h1 className="text-2xl font-bold mt-2">Infosec Digest — {date}</h1>
        <p className="text-gray-500 text-sm mt-1">{stories.length} stories</p>
      </div>

      {stories.length === 0 ? (
        <p className="text-gray-500">No individual stories could be parsed from this report.</p>
      ) : (
        <div className="space-y-4">
          {stories.map((story, i) => (
            <StoryCard key={i} story={story} />
          ))}
        </div>
      )}
    </div>
  );
}
