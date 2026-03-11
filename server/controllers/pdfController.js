const pdfParse = require("pdf-parse");
const fs = require("fs");
const StudyData = require("../models/StudyData");
const { generateStudyContent } = require("../utils/aiHelper");

const handleUpload = async (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ error: "No file uploaded" });

    const dataBuffer = fs.readFileSync(req.file.path);
    const pdfData = await pdfParse(dataBuffer);
    const extractedText = pdfData.text;

    fs.unlinkSync(req.file.path);

    const aiResponse = await generateStudyContent(extractedText);

    const saved = await StudyData.create({
      fileName: req.file.originalname,
      extractedText,
      ...aiResponse,
    });

    res.status(200).json({ success: true, data: saved });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
};

const getAllResults = async (req, res) => {
  try {
    const results = await StudyData.find().sort({ createdAt: -1 });
    res.json(results);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

const getResultById = async (req, res) => {
  try {
    const result = await StudyData.findById(req.params.id);
    if (!result) return res.status(404).json({ error: "Not found" });
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

module.exports = { handleUpload, getAllResults, getResultById };