const Anthropic = require("@anthropic-ai/sdk");
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const os = require("os");

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

async function extractJobData(jobPdfPath, photoFiles) {
  const pdfBase64 = fs.readFileSync(jobPdfPath).toString("base64");

  const content = [
    {
      type: "document",
      source: { type: "base64", media_type: "application/pdf", data: pdfBase64 }
    },
    {
      type: "text",
      text: `Extract all data from this Smith & Winters Electrical SimPRO job document. Return ONLY valid JSON with exactly these fields (use null for missing fields):
{
  "jobNo": "string",
  "customer": { "name": "string", "business": "string", "contact": "string", "phone": "string" },
  "siteAddress": "string",
  "salesperson": "string",
  "technician": "string",
  "worksDate": "string",
  "licence": "string",
  "abn": "string",
  "status": "string",
  "quoteRefs": ["string"],
  "certSafety": "string",
  "scopeItems": [{ "quoteRef": "string", "title": "string", "description": "string" }],
  "whatsIncluded": ["string"],
  "whatsNotIncluded": ["string"],
  "pricing": { "subtotalExGST": "string", "gst": "string", "totalIncGST": "string" },
  "notes": "string",
  "followUpRequired": false
}
Return ONLY the JSON object, no markdown, no explanation.`
    }
  ];

  const response = await client.messages.create({
    model: "claude-opus-4-5",
    max_tokens: 2000,
    messages: [{ role: "user", content }]
  });

  const raw = response.content.find(b => b.type === "text")?.text || "{}";
  try {
    return JSON.parse(raw.replace(/```json|```/g, "").trim());
  } catch (e) {
    throw new Error("Failed to parse job data from Claude response");
  }
}

async function buildPdf(jobData, photoFiles) {
  const tmpDir = os.tmpdir();
  const jsonPath = path.join(tmpDir, `job_${Date.now()}.json`);
  const outPath = path.join(tmpDir, `report_${Date.now()}.pdf`);
  const logoPath = path.join(__dirname, "..", "assets", "logo.png");

  const dataWithPhotos = {
    ...jobData,
    photoPaths: photoFiles.map(f => ({ path: f.path, originalname: f.originalname }))
  };
  fs.writeFileSync(jsonPath, JSON.stringify(dataWithPhotos, null, 2));

  const scriptPath = path.join(__dirname, "buildPdf.py");

  try {
    execSync(`python3 "${scriptPath}" "${jsonPath}" "${outPath}" "${logoPath}"`, {
      timeout: 120000,
      stdio: "pipe"
    });
  } catch (err) {
    const stderr = err.stderr?.toString() || "";
    const stdout = err.stdout?.toString() || "";
    throw new Error(`PDF build failed: ${stderr || stdout || err.message}`);
  }

  const pdfBuffer = fs.readFileSync(outPath);

  try { fs.unlinkSync(jsonPath); } catch {}
  try { fs.unlinkSync(outPath); } catch {}

  return pdfBuffer;
}

async function generateReport(jobPdfPath, photoFiles) {
  console.log(`Extracting job data from: ${jobPdfPath}`);
  console.log(`Photos included: ${photoFiles.length}`);
  const jobData = await extractJobData(jobPdfPath, photoFiles);
  console.log(`Job No: ${jobData.jobNo}, building PDF...`);
  return await buildPdf(jobData, photoFiles);
}

module.exports = { generateReport };
