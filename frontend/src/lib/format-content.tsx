"use client";

import React from "react";

// ---------------------------------------------------------------------------
// Block types
// ---------------------------------------------------------------------------

type Block =
  | { type: "heading"; level: 2 | 3; content: string }
  | { type: "paragraph"; content: string }
  | { type: "bullet-list"; items: string[] }
  | { type: "numbered-list"; items: { number: string; content: string }[] }
  | { type: "code-block"; language: string; content: string }
  | { type: "blockquote"; content: string }
  | { type: "horizontal-rule" }
  | { type: "table"; headers: string[]; rows: string[][] };

// ---------------------------------------------------------------------------
// Inline parser — handles bold, code, URLs within a text string
// ---------------------------------------------------------------------------

function parseInline(text: string, keyPrefix: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = [];
  let remaining = text;
  let partIdx = 0;

  while (remaining.length > 0) {
    // Inline code: `text`
    const codeMatch = remaining.match(/^`([^`]+)`/);
    if (codeMatch) {
      nodes.push(
        <code
          key={`${keyPrefix}-${partIdx++}`}
          className="px-1 py-0.5 rounded text-xs font-mono"
          style={{
            background: "rgba(124, 58, 237, 0.1)",
            color: "var(--color-accent-purple, #7c3aed)",
          }}
        >
          {codeMatch[1]}
        </code>
      );
      remaining = remaining.slice(codeMatch[0].length);
      continue;
    }

    // Bold: **text**
    const boldMatch = remaining.match(/^\*\*([^*]+)\*\*/);
    if (boldMatch) {
      nodes.push(
        <strong key={`${keyPrefix}-${partIdx++}`}>{boldMatch[1]}</strong>
      );
      remaining = remaining.slice(boldMatch[0].length);
      continue;
    }

    // URL: https://...
    const urlMatch = remaining.match(/^(https?:\/\/[^\s)]+)/);
    if (urlMatch) {
      nodes.push(
        <a
          key={`${keyPrefix}-${partIdx++}`}
          href={urlMatch[1]}
          target="_blank"
          rel="noopener noreferrer"
          className="underline"
          style={{ color: "var(--color-accent-purple, #7c3aed)" }}
        >
          {urlMatch[1]}
        </a>
      );
      remaining = remaining.slice(urlMatch[0].length);
      continue;
    }

    // Plain text — advance to the next special character
    const nextSpecial = remaining.search(/[`*]|https?:\/\//);
    if (nextSpecial === -1) {
      nodes.push(remaining);
      remaining = "";
    } else if (nextSpecial === 0) {
      // No match for formatting at this position — treat character as literal
      nodes.push(remaining[0]);
      remaining = remaining.slice(1);
    } else {
      nodes.push(remaining.slice(0, nextSpecial));
      remaining = remaining.slice(nextSpecial);
    }
  }

  return nodes;
}

// ---------------------------------------------------------------------------
// Block parser — converts raw text into typed Block array
// ---------------------------------------------------------------------------

function parseBlocks(text: string): Block[] {
  const blocks: Block[] = [];
  const lines = text.split("\n");
  let i = 0;

  // Accumulators for consecutive items
  let bulletItems: string[] | null = null;
  let numberedItems: { number: string; content: string }[] | null = null;
  let blockquoteLines: string[] | null = null;

  function flushBullet() {
    if (bulletItems && bulletItems.length > 0) {
      blocks.push({ type: "bullet-list", items: bulletItems });
      bulletItems = null;
    }
  }

  function flushNumbered() {
    if (numberedItems && numberedItems.length > 0) {
      blocks.push({ type: "numbered-list", items: numberedItems });
      numberedItems = null;
    }
  }

  function flushBlockquote() {
    if (blockquoteLines && blockquoteLines.length > 0) {
      blocks.push({ type: "blockquote", content: blockquoteLines.join("\n") });
      blockquoteLines = null;
    }
  }

  function flushAll() {
    flushBullet();
    flushNumbered();
    flushBlockquote();
  }

  while (i < lines.length) {
    const line = lines[i];

    // 1. Fenced code block
    const codeOpenMatch = line.match(/^```(\w*)/);
    if (codeOpenMatch) {
      flushAll();
      const language = codeOpenMatch[1] || "";
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].match(/^```\s*$/)) {
        codeLines.push(lines[i]);
        i++;
      }
      blocks.push({
        type: "code-block",
        language,
        content: codeLines.join("\n"),
      });
      i++; // skip closing ```
      continue;
    }

    // 2. Horizontal rule (---, ***, ___ with at least 3 chars)
    if (/^(\s*[-*_]\s*){3,}$/.test(line) && line.trim().length >= 3) {
      flushAll();
      blocks.push({ type: "horizontal-rule" });
      i++;
      continue;
    }

    // 3. Heading (## or ###)
    const headingMatch = line.match(/^(#{2,3})\s+(.+)$/);
    if (headingMatch) {
      flushAll();
      blocks.push({
        type: "heading",
        level: headingMatch[1].length as 2 | 3,
        content: headingMatch[2],
      });
      i++;
      continue;
    }

    // 4. Blockquote (> text)
    const bqMatch = line.match(/^>\s?(.*)/);
    if (bqMatch) {
      flushBullet();
      flushNumbered();
      if (!blockquoteLines) blockquoteLines = [];
      blockquoteLines.push(bqMatch[1]);
      i++;
      continue;
    } else {
      flushBlockquote();
    }

    // 5. Table row (| col1 | col2 |)
    const tableRowMatch = line.match(/^\|(.+)\|$/);
    if (tableRowMatch) {
      flushAll();
      // Accumulate table
      const headerCells = tableRowMatch[1].split("|").map((c) => c.trim());

      // Check if next line is separator
      if (i + 1 < lines.length && /^\|[\s\-:|]+\|$/.test(lines[i + 1])) {
        i += 2; // skip header + separator
        const dataRows: string[][] = [];
        while (i < lines.length) {
          const rowMatch = lines[i].match(/^\|(.+)\|$/);
          if (!rowMatch) break;
          const cells = rowMatch[1].split("|").map((c) => c.trim());
          // Normalize column count
          while (cells.length < headerCells.length) cells.push("");
          dataRows.push(cells.slice(0, headerCells.length));
          i++;
        }
        blocks.push({ type: "table", headers: headerCells, rows: dataRows });
      } else {
        // Not a valid table — treat as paragraph
        blocks.push({ type: "paragraph", content: line });
        i++;
      }
      continue;
    }

    // 6. Bullet list (- item or * item)
    const bulletMatch = line.match(/^\s*[-*]\s+(.+)$/);
    if (bulletMatch) {
      flushNumbered();
      flushBlockquote();
      if (!bulletItems) bulletItems = [];
      bulletItems.push(bulletMatch[1]);
      i++;
      continue;
    } else {
      flushBullet();
    }

    // 7. Numbered list (1. item or 1) item)
    const numMatch = line.match(/^\s*(\d+)[.)]\s+(.+)$/);
    if (numMatch) {
      flushBullet();
      flushBlockquote();
      if (!numberedItems) numberedItems = [];
      numberedItems.push({ number: numMatch[1], content: numMatch[2] });
      i++;
      continue;
    } else {
      flushNumbered();
    }

    // 8. Empty line
    if (line.trim() === "") {
      flushAll();
      i++;
      continue;
    }

    // 9. Paragraph (default)
    flushAll();
    blocks.push({ type: "paragraph", content: line });
    i++;
  }

  // Flush any remaining accumulators
  flushAll();

  return blocks;
}

// ---------------------------------------------------------------------------
// Block renderer — converts Block to JSX
// ---------------------------------------------------------------------------

function renderBlock(block: Block, index: number): React.ReactNode {
  const key = `block-${index}`;

  switch (block.type) {
    case "heading":
      return (
        <div
          key={key}
          style={{
            color: "var(--color-text-primary)",
            fontWeight: 600,
            fontSize: block.level === 2 ? "1rem" : "0.9rem",
            marginTop: index > 0 ? "0.75rem" : "0.25rem",
            marginBottom: "0.25rem",
            lineHeight: 1.3,
          }}
        >
          {parseInline(block.content, key)}
        </div>
      );

    case "paragraph":
      return (
        <p key={key} style={{ margin: "0.25rem 0" }}>
          {parseInline(block.content, key)}
        </p>
      );

    case "bullet-list":
      return (
        <div key={key} className="space-y-1 ml-1">
          {block.items.map((item, i) => (
            <div key={`${key}-${i}`} className="flex gap-1.5">
              <span
                className="shrink-0 mt-[0.45rem] w-1.5 h-1.5 rounded-full"
                style={{
                  background: "var(--color-accent-purple, #7c3aed)",
                }}
              />
              <span className="flex-1">
                {parseInline(item, `${key}-${i}`)}
              </span>
            </div>
          ))}
        </div>
      );

    case "numbered-list":
      return (
        <div key={key} className="space-y-1 ml-1">
          {block.items.map((item, i) => (
            <div key={`${key}-${i}`} className="flex gap-1.5">
              <span
                className="shrink-0 text-xs font-medium min-w-[1.25rem] text-right"
                style={{ color: "var(--color-accent-purple, #7c3aed)" }}
              >
                {item.number}.
              </span>
              <span className="flex-1">
                {parseInline(item.content, `${key}-${i}`)}
              </span>
            </div>
          ))}
        </div>
      );

    case "code-block":
      return (
        <div
          key={key}
          className="rounded-lg overflow-hidden my-1.5"
          style={{ border: "1px solid var(--color-border, #e5e7eb)" }}
        >
          {block.language && (
            <div
              className="px-3 py-1 text-[10px] font-mono uppercase tracking-wider"
              style={{
                background: "var(--color-bg-secondary, #f9fafb)",
                color: "var(--color-text-muted, #9ca3af)",
                borderBottom: "1px solid var(--color-border, #e5e7eb)",
              }}
            >
              {block.language}
            </div>
          )}
          <pre
            className="px-3 py-2 text-xs font-mono overflow-x-auto whitespace-pre-wrap"
            style={{
              background: "rgba(124, 58, 237, 0.04)",
              color: "var(--color-text-primary)",
              margin: 0,
            }}
          >
            <code>{block.content}</code>
          </pre>
        </div>
      );

    case "horizontal-rule":
      return (
        <hr
          key={key}
          className="my-2"
          style={{
            border: "none",
            borderTop: "1px solid var(--color-border, #e5e7eb)",
          }}
        />
      );

    case "blockquote":
      return (
        <div
          key={key}
          className="pl-3 my-1.5 py-1 text-sm"
          style={{
            borderLeft: "3px solid var(--color-accent-purple, #7c3aed)",
            background: "rgba(124, 58, 237, 0.04)",
            borderRadius: "0 6px 6px 0",
            color: "var(--color-text-secondary, #6b7280)",
          }}
        >
          {parseInline(block.content, key)}
        </div>
      );

    case "table":
      return (
        <div
          key={key}
          className="overflow-x-auto my-1.5 rounded-lg"
          style={{ border: "1px solid var(--color-border, #e5e7eb)" }}
        >
          <table className="w-full text-xs">
            <thead>
              <tr
                style={{
                  background: "var(--color-bg-secondary, #f9fafb)",
                }}
              >
                {block.headers.map((h, hi) => (
                  <th
                    key={hi}
                    className="px-2 py-1.5 text-left font-semibold"
                    style={{
                      borderBottom:
                        "1px solid var(--color-border, #e5e7eb)",
                      color: "var(--color-text-primary)",
                    }}
                  >
                    {parseInline(h, `${key}-th-${hi}`)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {block.rows.map((row, ri) => (
                <tr
                  key={ri}
                  style={{
                    background:
                      ri % 2 === 1
                        ? "rgba(0, 0, 0, 0.02)"
                        : "transparent",
                  }}
                >
                  {row.map((cell, ci) => (
                    <td
                      key={ci}
                      className="px-2 py-1.5"
                      style={{
                        borderBottom:
                          ri < block.rows.length - 1
                            ? "1px solid var(--color-border-light, #f1f5f9)"
                            : "none",
                        color: "var(--color-text-secondary)",
                      }}
                    >
                      {parseInline(cell, `${key}-${ri}-${ci}`)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );

    default:
      return null;
  }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export function formatContent(text: string): React.ReactNode[] {
  if (!text || !text.trim()) return [];
  const blocks = parseBlocks(text);
  return blocks.map((block, i) => renderBlock(block, i));
}
