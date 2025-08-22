"use client";

import { useState } from "react";

interface Section {
  heading: string;
  content: string;
}

interface Article {
  title: string;
  subtitle: string;
  sections: Section[];
}

export default function AdminPage() {
  const [topic, setTopic] = useState<string>("");
  const [article, setArticle] = useState<Article | null>(null);
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

      const text = await res.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        data = { error: "Cloud Run did not return valid JSON" };
      }

      if (data.error) {
        console.error("API error:", data.error);
        setArticle(null);
        return;
      }

      const articleObj: Article = {
        title: data.title || topic,
        subtitle: data.subtitle || "",
        sections: data.sections || [],
      };

      setArticle(articleObj);
      setArticlesList((prev) => [articleObj, ...prev]);
    } catch (err) {
      console.error(err);
      setArticle(null);
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

      {/* Show latest generated article */}
      {article && (
        <div style={{ marginTop: "2rem" }}>
          <h2>{article.title}</h2>
          {article.subtitle && <h4>{article.subtitle}</h4>}
          {article.sections.map((sec, idx) => (
            <div key={idx} style={{ marginTop: "1.5rem" }}>
              <h3>{sec.heading}</h3>
              <p>{sec.content}</p>
            </div>
          ))}
        </div>
      )}

      {/* History of generated articles */}
      {articlesList.length > 1 && (
        <div style={{ marginTop: "3rem" }}>
          <h2>History</h2>
          {articlesList.slice(1).map((a, i) => (
            <div key={i} style={{ marginTop: "2rem", borderTop: "1px solid #ccc", paddingTop: "1rem" }}>
              <h3>{a.title}</h3>
              {a.subtitle && <h5>{a.subtitle}</h5>}
              {a.sections.map((s, j) => (
                <div key={j} style={{ marginTop: "1rem" }}>
                  <h4>{s.heading}</h4>
                  <p>{s.content}</p>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
