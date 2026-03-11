const { OpenAI } = require("openai");

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const generateStudyContent = async (text) => {
  const prompt = `
You are an expert AI study assistant. Based on the following text extracted from a student's PDF, generate structured study content.

Return ONLY a valid JSON object with this exact structure:
{
  "predictedQuestions": ["question1", "question2", "question3", "question4", "question5"],
  "flashcards": [
    {"question": "...", "answer": "..."},
    {"question": "...", "answer": "..."},
    {"question": "...", "answer": "..."},
    {"question": "...", "answer": "..."},
    {"question": "...", "answer": "..."}
  ],
  "studyPlan": {
    "day1": "Topic and tasks for day 1",
    "day2": "Topic and tasks for day 2",
    "day3": "Topic and tasks for day 3",
    "day4": "Topic and tasks for day 4",
    "day5": "Topic and tasks for day 5",
    "day6": "Topic and tasks for day 6",
    "day7": "Topic and tasks for day 7"
  },
  "mockTest": [
    {"question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "answer": "A"},
    {"question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "answer": "B"},
    {"question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "answer": "C"},
    {"question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "answer": "A"},
    {"question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "answer": "D"}
  ]
}

Text:
${text.substring(0, 4000)}
  `;

  const response = await openai.chat.completions.create({
    model: "gpt-4",
    messages: [{ role: "user", content: prompt }],
    temperature: 0.7,
  });

  const raw = response.choices[0].message.content;
  return JSON.parse(raw);
};

module.exports = { generateStudyContent };