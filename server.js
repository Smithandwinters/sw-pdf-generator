hconst express = require("express");
const multer = require("multer");
const path = require("path");
const fs = require("fs");
const { generateReport } = require("./services/generateReport");

const app = express();
const PORT = process.env.PORT || 3000;

// Store uploads in /tmp which is always writable on Railway
const UPLOAD_DIR = path.join(require("os").tmpdir(), "sw_uploads");
if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR, { recursive: true });

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, UPLOAD_DIR);
  },
  filename: (req, file, cb) => {
    const unique = Date.now() + "-" + Math.round(Math.random() * 1e6);
    cb(null, unique + path.extname(file.originalname));
  }
});

const upload = multer({
  storage,
  limits: { fileSize: 50 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    const allowed = [".pdf", ".jpg", ".jpeg", ".png", ".webp"];
    const ext = path.extname(file.originalname).toLowerCase();
    if (allowed.includes(ext)) cb(null, true);
    else cb(new Error("File type not allowed: " + ext));
  }
});

app.use(express.static(path.join(__dirname, "public")));

// Serve logo from assets folder
app.use("/logo.png", express.static(path.join(__dirname, "assets", "logo.png")));

app.post("/generate-pdf",
  upload.fields([{ name: "jobPdf", maxCount: 1 }, { name: "photos", maxCount: 50 }]),
  async (req, res) => {
    const jobPdfFile = req.files?.jobPdf?.[0];
    const photoFiles = req.files?.photos || [];

    console.log("Received jobPdf:", jobPdfFile?.path);
    console.log("Received photos:", photoFiles.length, photoFiles.map(f => f.path));

    if (!jobPdfFile) {
      return res.status(400).json({ error: "jobPdf is required" });
    }

    // Collect ALL uploaded file paths for cleanup after
    const allPaths = [jobPdfFile.path, ...photoFiles.map(f => f.path)];

    try {
      const pdfBuffer = await generateReport(jobPdfFile.path, photoFiles);

      const baseName = path.basename(jobPdfFile.originalname, ".pdf");
      const outName = "SW_Completion_" + baseName + "_" + Date.now() + ".pdf";

      res.setHeader("Content-Type", "application/pdf");
      res.setHeader("Content-Disposition", `attachment; filename="${outName}"`);
      res.send(pdfBuffer);

    } catch (err) {
      console.error("Generation error:", err.message);
      res.status(500).json({ error: err.message });
    } finally {
      // Clean up AFTER response is sent
      for (const p of allPaths) {
        try { fs.unlinkSync(p); } catch {}
      }
    }
  }
);

app.get("/health", (req, res) => res.json({ status: "ok" }));

app.listen(PORT, () => console.log("Smith & Winters PDF Generator running on port " + PORT));
