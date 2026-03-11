const mongoose = require("mongoose");

const StudyDataSchema = new mongoose.Schema(
  {
    fileName: { type: String, required: true },
    extractedText: { type: String },
    predictedQuestions: [String],
    flashcards: [
      {
        question: String,
        answer: String,
      },
    ],
    studyPlan: { type: Object },
    mockTest: [
      {
        question: String,
        options: [String],
        answer: String,
      },
    ],
  },
  { timestamps: true }
);

module.exports = mongoose.model("StudyData", StudyDataSchema);