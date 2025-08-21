import { NextResponse } from "next/server";

interface GenerateRequest {
  topic: string;
}

export async function POST(req: Request) {
  try {
    const body: GenerateRequest = await req.json();
    const { topic } = body;
    if (!topic) return NextResponse.json({ error: "Topic is required" }, { status: 400 });

    const agentUrl = process.env.NEWS_AGENT_URL!;
    const cloudRunRes = await fetch(agentUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic }),
    });

    const text = await cloudRunRes.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      data = { error: "Cloud Run did not return valid JSON", html: text };
    }

    return NextResponse.json(data);
  } catch (err) {
    console.error(err);
    return NextResponse.json({ error: "Failed to generate article" }, { status: 500 });
  }
}
