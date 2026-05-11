import { Storage } from "@google-cloud/storage";

const DIGEST_SUFFIX = "_infosec_digest.md";

let _storage: Storage | null = null;

function storage(): Storage {
  if (!_storage) _storage = new Storage();
  return _storage;
}

function bucket() {
  const name = process.env.GCS_BUCKET_NAME;
  if (!name) throw new Error("GCS_BUCKET_NAME is not set");
  return storage().bucket(name);
}

export interface DigestMeta {
  slug: string;
  date: string;
  filename: string;
}

export async function listDigests(): Promise<DigestMeta[]> {
  const [blobs] = await bucket().getFiles();
  return blobs
    .filter((b) => b.name.endsWith(DIGEST_SUFFIX))
    .sort((a, b) => b.name.localeCompare(a.name))
    .map((b) => {
      const slug = b.name.replace(DIGEST_SUFFIX, "");
      return { slug, date: formatDate(slug), filename: b.name };
    });
}

export async function getDigest(slug: string): Promise<string> {
  const filename = `${slug}${DIGEST_SUFFIX}`;
  const [content] = await bucket().file(filename).download();
  return content.toString("utf-8");
}

export async function saveEscalation(
  slug: string,
  content: string
): Promise<string> {
  const filename = `escalations/${slug}.md`;
  await bucket().file(filename).save(content, { contentType: "text/markdown" });
  return filename;
}

function formatDate(slug: string): string {
  const match = slug.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) return slug;
  const d = new Date(`${slug}T00:00:00Z`);
  return d.toLocaleDateString("en-GB", {
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  });
}
