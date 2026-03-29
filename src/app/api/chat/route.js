import OpenAI from 'openai';

const openai = new OpenAI({
    baseURL: "https://openrouter.ai/api/v1",
    apiKey: process.env.OPENROUTER_API_KEY || 'sk-placeholder',
    defaultHeaders: {
        "HTTP-Referer": "https://localhost:3000",
        "X-Title": "Mock Interview Chatbot",
    }
});

// Python backend URL (local server with Beyond Presence)
const WEBHOOK_URL = 'http://localhost:5000/webhook';

// System prompt to guide the AI
const SYSTEM_PROMPT = `
You are a friendly and professional mock interview recruiter assistant.
Your goal is to collect the following 4 pieces of information from the user:
1. Full Name
2. Email Address
3. Job they are applying for
4. Resume (The user must upload a document. If you receive a message with the content "[User uploaded resume: <URL>]", treat that as the resume).

Instructions:
- **CRITICAL**: If you see a message starting with "[User uploaded resume: ...]", this IS the resume. The URL is inside.
- **CRITICAL**: The generated JSON MUST be valid.
- Ask for one piece of information at a time.
- Be conversational and polite.
- When you have ALL 4 pieces of information (Name, Email, Job, Resume), you MUST send a specific closing message AND the collected data in JSON format.
- **CLOSING MESSAGE**: Exactly consist of this text (replace [email] with their actual email):
  "Thanks for submitting your resume. Our HR will send you a mail within two minutes to your registered mail ID [email]. Thank you and all the best for your interview."
- **JSON BLOCK**: Must be at the VERY END of your response, strictly following this format:
\`\`\`json
{
  "collected_data": {
    "name": "User Name",
    "email": "user@email.com",
    "job": "Job Title",
    "resume_link": "<THE_EXACT_URL_FROM_THE_MESSAGE>"
  }
}
\`\`\`
- Do NOT output the JSON block until you have all 4 items.
- **Trigger Condition**: As soon as you have the 4th item (likely the resume), you MUST output the JSON block in that very same response.
`;

export async function POST(req) {
    try {
        const body = await req.json();
        const headers = { 'Content-Type': 'application/json' };
        const { messages } = body;

        console.log("--- CHAT ENDPOINT TRIGGERED ---");
        // console.log("Incoming Messages History:", JSON.stringify(messages, null, 2));

        const completion = await openai.chat.completions.create({
            model: "openai/gpt-4o-mini",
            messages: [
                { role: "system", content: SYSTEM_PROMPT },
                ...messages
            ],
            temperature: 0.1, // Lower temperature for more deterministic formatting
        });

        const aiResponse = completion.choices[0].message.content;
        console.log("--- AI RAW RESPONSE START ---");
        console.log(aiResponse);
        console.log("--- AI RAW RESPONSE END ---");

        // Strategy 1: Look for code block
        let jsonStr = null;
        const codeBlockMatch = aiResponse.match(/```(?:json)?\s*([\s\S]*?)\s*```/);

        if (codeBlockMatch) {
            jsonStr = codeBlockMatch[1];
        } else {
            // Strategy 2: Look for raw JSON object if code block missing
            console.log("No code block found. Attempting to find raw JSON...");
            const jsonObjectMatch = aiResponse.match(/(\{[\s\S]*"collected_data"[\s\S]*\})/);
            if (jsonObjectMatch) {
                jsonStr = jsonObjectMatch[1];
            }
        }

        if (jsonStr) {
            try {
                const jsonData = JSON.parse(jsonStr.trim());
                if (jsonData.collected_data) {
                    console.log("Valid JSON Data Found:", jsonData.collected_data);

                    // Clean the response: Remove the JSON part
                    // We remove everything from the start of the match to the end
                    let cleanResponse = aiResponse;
                    if (codeBlockMatch) {
                        cleanResponse = aiResponse.replace(codeBlockMatch[0], '').trim();
                    } else if (jsonStr) {
                        cleanResponse = aiResponse.replace(jsonStr, '').trim();
                    }

                    // Call Python Backend
                    console.log("Calling Python backend:", WEBHOOK_URL);

                    try {
                        const webhookRes = await fetch(WEBHOOK_URL, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                name: jsonData.collected_data.name,
                                email: jsonData.collected_data.email,
                                job: jsonData.collected_data.job,
                                resume_link: jsonData.collected_data.resume_link || ""
                            })
                        });

                        console.log("Backend Status:", webhookRes.status);

                        if (webhookRes.ok) {
                            const backendData = await webhookRes.json();
                            console.log("Backend Response:", backendData);

                            return new Response(JSON.stringify({
                                content: cleanResponse,
                                redirectUrl: backendData.url
                            }), { status: 200, headers });
                        } else {
                            console.error("Backend failed:", webhookRes.status);
                        }
                    } catch (backendError) {
                        console.error("Failed to call backend:", backendError);
                    }
                }
            } catch (e) {
                console.error("Error parsing extract JSON or calling webhook", e);
            }
        } else {
            console.log("No JSON structure found in AI response.");
        }

        return new Response(JSON.stringify({ content: aiResponse }), { status: 200, headers });

    } catch (error) {
        console.error('Error in chat route:', error);
        return new Response(JSON.stringify({ error: 'Internal Server Error' }), { status: 500 });
    }
}
