import { VertexAI } from "@google-cloud/vertexai";

const PROJECT = process.env.GOOGLE_CLOUD_PROJECT ?? "the-tinkering-shed";
const LOCATION = process.env.GOOGLE_CLOUD_LOCATION ?? "europe-west2";
const MODEL = "gemini-2.0-flash";

export async function generateEscalationReport(
  title: string,
  url: string,
  published: string,
  summary: string
): Promise<string> {
  const vertexAI = new VertexAI({ project: PROJECT, location: LOCATION });
  const model = vertexAI.getGenerativeModel({ model: MODEL });

  const today = new Date().toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });

  const storyContent = `Title: ${title}
URL: ${url}
Published: ${published}
Summary: ${summary}`;

  const prompt = `You are a cybersecurity analyst at a UK financial services organisation. You are writing an executive escalation report based on the following infosec news story.

Story:
${storyContent}

Generate a structured escalation report in exactly this markdown format. Fill in each section based on your analysis. Do not include any text outside this structure.

# ${title}

## Executive Summary
<At most one paragraph explaining the risk in terms a technically aware C-suite member (CIO, CISO, CFO) will understand. Focus on business risk, not technical jargon.>

**Date raised:** ${today}
**Risk rating:** High | Medium
**Likelihood:** High | Medium | Low
**Impact:** Material | Moderate | Low
**Media attention:** Mainstream | Tech industry | None
**Status:** Actions in plan

## Further Detail
<Explain in technical detail how the vulnerability works and how it could be exploited against a UK financial services organisation.>

## Impact
<Explain what could happen in the worst case if this vulnerability were exploited against the organisation.>

## Likelihood
<Explain how likely this vulnerability is to be exploited — consider threat landscape, attacker motivation, and prevalence.>

## Current Status
<Describe initial steps taken upon learning of this vulnerability: reviewing affected systems, notifying relevant teams, beginning initial assessment.>

## Remediation
<Suggest 3–5 concrete, actionable steps to mitigate the threat.>

## References
- [${title}](${url})
`;

  const result = await model.generateContent(prompt);
  const response = result.response;
  const text = response.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) throw new Error("Empty response from Vertex AI");
  return text.trim();
}

export function escalationFilename(title: string): string {
  const today = new Date().toISOString().slice(0, 10);
  const slug = title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 60);
  return `${today}_${slug}`;
}
