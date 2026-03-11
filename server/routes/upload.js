const express = require("express");
const multer = require("multer");
const { handleUpload, getAllResults, getResultById } = require("../controllers/pdfController");

const router = express.Router();
const upload = multer({ dest: "uploads/" });

router.post("/upload", upload.single("pdf"), handleUpload);
router.get("/results", getAllResults);
router.get("/results/:id", getResultById);

module.exports = router;
