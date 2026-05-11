export interface Story {
  title: string;
  url: string;
  published: string;
  summary: string;
  source: "register" | "sans" | "unknown";
  raw: string;
}

export function parseStories(markdown: string): Story[] {
  const stories: Story[] = [];

  // Split into broad sections by ## headings
  const sections = markdown.split(/\n(?=## )/);

  for (const section of sections) {
    const isRegister = /## The Register/i.test(section);
    const isSans = /## SANS ISC/i.test(section);
    if (!isRegister && !isSans) continue;

    const source: Story["source"] = isRegister ? "register" : "sans";

    // Each story starts with **[Title](url)**
    const storyBlocks = section.split(/\n(?=\*\*\[)/);

    for (const block of storyBlocks) {
      const trimmed = block.trim();
      if (!trimmed.startsWith("**[")) continue;

      const titleMatch = trimmed.match(/^\*\*\[([^\]]+)\]\(([^)]+)\)\*\*/);
      if (!titleMatch) continue;

      const [, title, url] = titleMatch;

      const publishedMatch = trimmed.match(/\*Published:\s*([^*\n]+)\*/);
      const published = publishedMatch ? publishedMatch[1].trim() : "";

      // Summary is everything after the published line (or title line if no date)
      const lines = trimmed.split("\n");
      const summaryLines: string[] = [];
      let pastHeader = false;
      for (const line of lines) {
        if (!pastHeader) {
          if (line.startsWith("**[") || line.startsWith("*Published:")) {
            pastHeader = line.startsWith("*Published:");
            continue;
          }
        }
        if (pastHeader && line.trim()) summaryLines.push(line.trim());
      }

      stories.push({
        title,
        url,
        published,
        summary: summaryLines.join(" ").trim(),
        source,
        raw: trimmed,
      });
    }
  }

  return stories;
}
