"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeSanitize from "rehype-sanitize";
import type { Pluggable } from "unified";

interface Article {
  topic: string;
  markdown: string;
}

export default function AdminPage() {
  const [topic, setTopic] = useState<string>("");
  const [article, setArticle] = useState<string>("");
  const [articlesList, setArticlesList] = useState<Article[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const generateArticle = async () => {
    if (!topic) return;
    setLoading(true);

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic }),
      });

      // Read text first, then parse JSON safely
      const text = await res.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        data = { markdown: "Error: Cloud Run did not return valid JSON" };
      }

      const markdown = data.markdown || data.text || JSON.stringify(data);
      setArticle(markdown);

      setArticlesList((prev) => [{ topic, markdown }, ...prev]);
    } catch (err) {
      console.error(err);
      setArticle("Error generating article");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
      <h1>AI News Admin</h1>

      <div style={{ marginBottom: "1rem" }}>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter topic"
          style={{ width: "60%", padding: "0.5rem" }}
        />
        <button
          onClick={generateArticle}
          style={{ marginLeft: "1rem", padding: "0.5rem 1rem" }}
        >
          {loading ? "Generating..." : "Generate"}
        </button>
      </div>

      {article && (
        <div
          style={{
            marginTop: "2rem",
            border: "1px solid #ccc",
            padding: "1rem",
            borderRadius: "6px",
            backgroundColor: "#f9f9f9",
          }}
        >
          <h2>Generated Article</h2>
          <ReactMarkdown rehypePlugins={[rehypeSanitize]}>{article}</ReactMarkdown>
        </div>
      )}

      {articlesList.length > 0 && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Saved Articles</h2>
          {articlesList.map((a, idx) => (
            <div
              key={idx}
              style={{
                border: "1px solid #ccc",
                padding: "1rem",
                marginBottom: "1rem",
                borderRadius: "6px",
                backgroundColor: "#fefefe",
              }}
            >
              <h3>{a.topic}</h3>
              <ReactMarkdown rehypePlugins={[rehypeSanitize as Pluggable]}>
                {a.markdown}
              </ReactMarkdown>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
