"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { useAuth } from "@/lib/auth-context";
import Link from "next/link";
import {
  getCompanies,
  getDataRoomFolders,
  createDataRoomFolder,
  getDataRoomFiles,
  uploadDataRoomFile,
  downloadDataRoomFile,
  createShareLink,
  getShareLinks,
  setupDefaultDataRoom,
  getRetentionAlerts,
  getRetentionSummary,
} from "@/lib/api";


// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Folder {
  id: number;
  name: string;
  description: string | null;
  parent_id: number | null;
  file_count: number;
  created_at: string;
}

interface DataFile {
  id: number;
  filename: string;
  original_filename: string;
  size: number;
  mime_type: string;
  folder_id: number;
  description: string | null;
  tags: string[];
  retention_category: string | null;
  retention_expiry: string | null;
  uploaded_at: string;
}

interface ShareLinkItem {
  id: number;
  name: string;
  url: string;
  token: string;
  password_protected: boolean;
  expires_at: string | null;
  max_downloads: number | null;
  download_count: number;
  is_active: boolean;
  created_at: string;
}

interface RetentionAlert {
  file_id: number;
  filename: string;
  retention_category: string;
  expiry_date: string;
  days_remaining: number;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const RETENTION_BADGES: Record<string, { bg: string; text: string; label: string }> = {
  PERMANENT: { bg: "bg-purple-500/10 border-purple-500/30", text: "text-purple-400", label: "Permanent" },
  "8_YEARS": { bg: "bg-blue-500/10 border-blue-500/30", text: "text-blue-400", label: "8 Years" },
  "6_YEARS": { bg: "bg-amber-500/10 border-amber-500/30", text: "text-amber-400", label: "6 Years" },
  "3_YEARS": { bg: "bg-emerald-500/10 border-emerald-500/30", text: "text-emerald-400", label: "3 Years" },
  CUSTOM: { bg: "bg-gray-500/10 border-gray-500/30", text: "", label: "Custom" },
};

const TAG_OPTIONS = ["legal", "compliance", "financial", "tax", "ip", "hr", "corporate"];

const RETENTION_OPTIONS = [
  { value: "PERMANENT", label: "Permanent" },
  { value: "8_YEARS", label: "8 Years (Books of Accounts)" },
  { value: "6_YEARS", label: "6 Years (Tax Records)" },
  { value: "3_YEARS", label: "3 Years (DPDP)" },
  { value: "CUSTOM", label: "Custom" },
];

function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function DataRoomPage() {
  const { user, loading: authLoading } = useAuth();

  const [companies, setCompanies] = useState<any[]>([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  // Data
  const [folders, setFolders] = useState<Folder[]>([]);
  const [files, setFiles] = useState<DataFile[]>([]);
  const [shareLinks, setShareLinks] = useState<ShareLinkItem[]>([]);
  const [retentionAlerts, setRetentionAlerts] = useState<RetentionAlert[]>([]);
  const [retentionSummary, setRetentionSummary] = useState<any>(null);

  // UI state
  const [selectedFolderId, setSelectedFolderId] = useState<number | null>(null);
  const [showCreateFolder, setShowCreateFolder] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [showShareForm, setShowShareForm] = useState(false);
  const [message, setMessage] = useState("");
  const [actionLoading, setActionLoading] = useState(false);
  const [dragging, setDragging] = useState(false);

  // Create folder form
  const [newFolderName, setNewFolderName] = useState("");
  const [newFolderDescription, setNewFolderDescription] = useState("");

  // Upload form
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadDescription, setUploadDescription] = useState("");
  const [uploadTags, setUploadTags] = useState<string[]>([]);
  const [uploadRetention, setUploadRetention] = useState("PERMANENT");
  const [uploadCustomDate, setUploadCustomDate] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Share link form
  const [shareName, setShareName] = useState("");
  const [sharePassword, setSharePassword] = useState("");
  const [shareExpiry, setShareExpiry] = useState("");
  const [shareMaxDownloads, setShareMaxDownloads] = useState("");
  const [shareFileIds, setShareFileIds] = useState<number[]>([]);

  // Fetch companies
  useEffect(() => {
    if (authLoading || !user) return;
    getCompanies()
      .then((comps) => {
        setCompanies(comps);
        if (comps.length > 0) setSelectedCompanyId(comps[0].id);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [user, authLoading]);

  // Fetch data room data
  const fetchDataRoomData = useCallback(async () => {
    if (!selectedCompanyId) return;
    try {
      const [foldersRes, filesRes, linksRes, alertsRes, summaryRes] = await Promise.allSettled([
        getDataRoomFolders(selectedCompanyId),
        getDataRoomFiles(selectedCompanyId),
        getShareLinks(selectedCompanyId),
        getRetentionAlerts(selectedCompanyId),
        getRetentionSummary(selectedCompanyId),
      ]);

      if (foldersRes.status === "fulfilled") {
        const fld = Array.isArray(foldersRes.value) ? foldersRes.value : foldersRes.value?.folders || [];
        setFolders(fld);
        if (fld.length > 0 && !selectedFolderId) {
          setSelectedFolderId(fld[0].id);
        }
      }
      if (filesRes.status === "fulfilled") {
        setFiles(Array.isArray(filesRes.value) ? filesRes.value : filesRes.value?.files || []);
      }
      if (linksRes.status === "fulfilled") {
        setShareLinks(Array.isArray(linksRes.value) ? linksRes.value : linksRes.value?.links || []);
      }
      if (alertsRes.status === "fulfilled") {
        setRetentionAlerts(Array.isArray(alertsRes.value) ? alertsRes.value : alertsRes.value?.alerts || []);
      }
      if (summaryRes.status === "fulfilled") {
        setRetentionSummary(summaryRes.value);
      }
    } catch (err) {
      console.error("Failed to fetch data room:", err);
    }
  }, [selectedCompanyId, selectedFolderId]);

  useEffect(() => {
    if (!selectedCompanyId) return;
    setLoading(true);
    fetchDataRoomData().finally(() => setLoading(false));
  }, [selectedCompanyId, fetchDataRoomData]);

  // Files in selected folder
  const folderFiles = selectedFolderId
    ? files.filter((f) => f.folder_id === selectedFolderId)
    : files;

  // Setup defaults
  const handleSetupDefaults = async () => {
    if (!selectedCompanyId) return;
    setActionLoading(true);
    try {
      await setupDefaultDataRoom(selectedCompanyId);
      setMessage("Default folders created successfully.");
      await fetchDataRoomData();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  // Create folder
  const handleCreateFolder = async () => {
    if (!selectedCompanyId || !newFolderName.trim()) return;
    setActionLoading(true);
    try {
      await createDataRoomFolder(selectedCompanyId, {
        name: newFolderName.trim(),
        description: newFolderDescription.trim() || null,
        parent_id: null,
      });
      setMessage("Folder created successfully.");
      setShowCreateFolder(false);
      setNewFolderName("");
      setNewFolderDescription("");
      await fetchDataRoomData();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  // Upload file
  const handleUpload = async (file?: File) => {
    const fileToUpload = file || uploadFile;
    if (!selectedCompanyId || !selectedFolderId || !fileToUpload) return;
    setActionLoading(true);
    try {
      await uploadDataRoomFile(selectedCompanyId, selectedFolderId, fileToUpload, {
        description: uploadDescription.trim() || undefined,
        tags: uploadTags.length > 0 ? uploadTags : undefined,
        retention_category: uploadRetention,
      });
      setMessage("File uploaded successfully.");
      setShowUpload(false);
      setUploadFile(null);
      setUploadDescription("");
      setUploadTags([]);
      setUploadRetention("PERMANENT");
      await fetchDataRoomData();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  // Download file
  const handleDownload = async (file: DataFile) => {
    if (!selectedCompanyId) return;
    try {
      const blob = await downloadDataRoomFile(selectedCompanyId, file.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = file.original_filename || file.filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download failed:", err);
      setMessage("Error: Download failed.");
    }
  };

  // Create share link
  const handleCreateShareLink = async () => {
    if (!selectedCompanyId || !shareName.trim()) return;
    setActionLoading(true);
    try {
      await createShareLink(selectedCompanyId, {
        name: shareName.trim(),
        password: sharePassword || undefined,
        expires_at: shareExpiry || undefined,
        max_downloads: shareMaxDownloads ? parseInt(shareMaxDownloads) : undefined,
        file_ids: shareFileIds.length > 0 ? shareFileIds : undefined,
        folder_id: selectedFolderId,
      });
      setMessage("Share link created successfully.");
      setShowShareForm(false);
      setShareName("");
      setSharePassword("");
      setShareExpiry("");
      setShareMaxDownloads("");
      setShareFileIds([]);
      await fetchDataRoomData();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  // Drag & Drop handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => {
    setDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && selectedFolderId) {
      setUploadFile(droppedFile);
      setShowUpload(true);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setMessage("Link copied to clipboard.");
    setTimeout(() => setMessage(""), 2000);
  };

  // Loading / Auth
  if (authLoading || (loading && folders.length === 0 && files.length === 0)) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="animate-pulse-glow w-16 h-16 rounded-full flex items-center justify-center" style={{ background: "rgba(139, 92, 246, 0.2)" }}>
          <img src="/logo-icon.png" alt="Anvils" className="w-7 h-7 object-contain" />
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 gap-4 animate-fade-in-up">
          <div>
            <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>
              Data Room
            </h1>
            <p className="text-sm border-l-2 pl-3 border-purple-500" style={{ color: "var(--color-text-secondary)" }}>
              Secure document vault with investor sharing
            </p>
          </div>
          <div className="flex items-center gap-3 flex-wrap">
            {companies.length > 1 && (
              <select
                className="glass-card text-sm px-3 py-2 rounded-lg border-none outline-none"
                style={{ background: "var(--color-bg-card)", color: "var(--color-text-primary)" }}
                value={selectedCompanyId || ""}
                onChange={(e) => {
                  setSelectedCompanyId(Number(e.target.value));
                  setSelectedFolderId(null);
                }}
              >
                {companies.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.approved_name || c.proposed_names?.[0] || `Company #${c.id}`}
                  </option>
                ))}
              </select>
            )}
            {folders.length === 0 && (
              <button
                onClick={handleSetupDefaults}
                disabled={actionLoading}
                className="text-sm font-medium border border-emerald-500/30 text-emerald-400 px-4 py-2 rounded-lg hover:bg-emerald-500/10 transition-colors"
              >
                Setup Default Folders
              </button>
            )}
            <button
              onClick={() => { setShowCreateFolder(true); setMessage(""); }}
              className="text-sm font-medium border px-4 py-2 rounded-lg transition-colors"
              style={{ color: "var(--color-text-secondary)", borderColor: "var(--color-border)" }}
            >
              + Create Folder
            </button>
            <button
              onClick={() => { setShowShareForm(true); setMessage(""); }}
              className="btn-primary text-sm !py-2 !px-4"
            >
              + Share Link
            </button>
          </div>
        </div>

        {/* Message */}
        {message && (
          <div className={`p-3 mb-6 rounded-lg text-sm text-center border animate-fade-in-up ${
            message.startsWith("Error")
              ? "border-red-500/30 bg-red-500/5 text-red-400"
              : "border-emerald-500/30 bg-emerald-500/5 text-emerald-400"
          }`}>
            {message}
          </div>
        )}

        {companies.length === 0 ? (
          <div className="p-12 text-center" style={{ background: "var(--color-bg-card)" }}>
            <h2 className="text-xl font-bold mb-2" style={{ color: "var(--color-text-primary)" }}>No company selected</h2>
            <p className="text-sm mb-6" style={{ color: "var(--color-text-secondary)" }}>
              Select a company from the sidebar to view data room files and documents.
            </p>
            <div className="flex items-center justify-center gap-3">
              <Link href="/pricing" className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white" style={{ background: "#8B5CF6" }}>
                Incorporate a New Company
              </Link>
              <Link href="/dashboard/connect" className="px-5 py-2.5 rounded-lg text-sm font-semibold border" style={{ borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}>
                Connect Existing Company
              </Link>
            </div>
          </div>
        ) : (
          <>
            {/* Create Folder Form */}
            {showCreateFolder && (
              <div className="glass-card p-6 mb-6 animate-fade-in-up" style={{ cursor: "default" }}>
                <h3 className="text-sm font-semibold mb-4">Create New Folder</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>Folder Name *</label>
                    <input
                      type="text"
                      value={newFolderName}
                      onChange={(e) => setNewFolderName(e.target.value)}
                      placeholder="e.g., Legal Documents"
                      className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                      style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>Description</label>
                    <input
                      type="text"
                      value={newFolderDescription}
                      onChange={(e) => setNewFolderDescription(e.target.value)}
                      placeholder="Optional description"
                      className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                      style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                    />
                  </div>
                </div>
                <div className="flex gap-3">
                  <button onClick={handleCreateFolder} disabled={actionLoading || !newFolderName.trim()} className="btn-primary text-sm !py-2 !px-6">
                    {actionLoading ? "Creating..." : "Create Folder"}
                  </button>
                  <button onClick={() => { setShowCreateFolder(false); setNewFolderName(""); setNewFolderDescription(""); }} className="text-sm px-4 py-2 rounded-lg border transition-colors" style={{ color: "var(--color-text-secondary)", borderColor: "var(--color-border)" }}>
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {/* Share Link Form */}
            {showShareForm && (
              <div className="glass-card p-6 mb-6 animate-fade-in-up" style={{ cursor: "default" }}>
                <h3 className="text-sm font-semibold mb-4">Create Share Link</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>Link Name *</label>
                    <input
                      type="text"
                      value={shareName}
                      onChange={(e) => setShareName(e.target.value)}
                      placeholder="e.g., Series A Due Diligence"
                      className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                      style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>Password (optional)</label>
                    <input
                      type="text"
                      value={sharePassword}
                      onChange={(e) => setSharePassword(e.target.value)}
                      placeholder="Leave empty for no password"
                      className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                      style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>Expiry Date (optional)</label>
                    <input
                      type="date"
                      value={shareExpiry}
                      onChange={(e) => setShareExpiry(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                      style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>Max Downloads (optional)</label>
                    <input
                      type="number"
                      value={shareMaxDownloads}
                      onChange={(e) => setShareMaxDownloads(e.target.value)}
                      placeholder="Unlimited"
                      className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                      style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                    />
                  </div>
                </div>
                <div className="flex gap-3">
                  <button onClick={handleCreateShareLink} disabled={actionLoading || !shareName.trim()} className="btn-primary text-sm !py-2 !px-6">
                    {actionLoading ? "Creating..." : "Create Link"}
                  </button>
                  <button onClick={() => { setShowShareForm(false); setShareName(""); setSharePassword(""); setShareExpiry(""); setShareMaxDownloads(""); }} className="text-sm px-4 py-2 rounded-lg border transition-colors" style={{ color: "var(--color-text-secondary)", borderColor: "var(--color-border)" }}>
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {/* Main content: Folder sidebar + Files */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8 animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
              {/* Folder Sidebar */}
              <div className="lg:col-span-1">
                <div className="glass-card p-4" style={{ cursor: "default" }}>
                  <h3 className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: "var(--color-text-muted)" }}>
                    Folders
                  </h3>
                  {folders.length === 0 ? (
                    <p className="text-xs py-4 text-center" style={{ color: "var(--color-text-muted)" }}>
                      No folders yet. Setup defaults or create one.
                    </p>
                  ) : (
                    <div className="space-y-1">
                      <button
                        onClick={() => setSelectedFolderId(null)}
                        className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${
                          selectedFolderId === null
                            ? "bg-purple-500/20 text-purple-400"
                            : ""
                        }`}
                        style={selectedFolderId !== null ? { color: "var(--color-text-secondary)" } : {}}
                      >
                        <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z" />
                        </svg>
                        All Files
                        <span className="text-[10px] ml-auto" style={{ color: "var(--color-text-muted)" }}>{files.length}</span>
                      </button>
                      {folders.map((folder) => (
                        <button
                          key={folder.id}
                          onClick={() => setSelectedFolderId(folder.id)}
                          className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${
                            selectedFolderId === folder.id
                              ? "bg-purple-500/20 text-purple-400"
                              : ""
                          }`}
                          style={selectedFolderId !== folder.id ? { color: "var(--color-text-secondary)" } : {}}
                        >
                          <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z" />
                          </svg>
                          <span className="truncate">{folder.name}</span>
                          <span className="text-[10px] ml-auto shrink-0" style={{ color: "var(--color-text-muted)" }}>{folder.file_count ?? 0}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Files Content Area */}
              <div className="lg:col-span-3">
                <div className="glass-card p-6" style={{ cursor: "default" }}>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-semibold">
                      {selectedFolderId
                        ? folders.find((f) => f.id === selectedFolderId)?.name || "Files"
                        : "All Files"}
                    </h3>
                    {selectedFolderId && (
                      <button
                        onClick={() => { setShowUpload(true); setMessage(""); }}
                        className="text-xs font-medium border border-purple-500/30 text-purple-400 px-3 py-1.5 rounded-lg hover:bg-purple-500/10 transition-colors"
                      >
                        + Upload File
                      </button>
                    )}
                  </div>

                  {/* Upload Form */}
                  {showUpload && selectedFolderId && (
                    <div className="p-5 rounded-lg border border-purple-500/20 bg-purple-500/5 mb-6">
                      <h4 className="text-sm font-semibold mb-4">Upload File</h4>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>File *</label>
                          <input
                            ref={fileInputRef}
                            type="file"
                            onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                            className="w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-purple-500/20 file:text-purple-400 hover:file:bg-purple-500/30"
                            style={{ color: "var(--color-text-secondary)" }}
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>Description</label>
                          <input
                            type="text"
                            value={uploadDescription}
                            onChange={(e) => setUploadDescription(e.target.value)}
                            placeholder="Brief description"
                            className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                            style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: "var(--color-text-muted)" }}>Tags</label>
                          <div className="flex flex-wrap gap-2">
                            {TAG_OPTIONS.map((tag) => (
                              <button
                                key={tag}
                                type="button"
                                onClick={() => {
                                  setUploadTags((prev) =>
                                    prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
                                  );
                                }}
                                className={`text-xs px-2.5 py-1 rounded-full border transition-colors ${
                                  uploadTags.includes(tag)
                                    ? "bg-purple-500/20 text-purple-400 border-purple-500/30"
                                    : ""
                                }`}
                                style={!uploadTags.includes(tag) ? { color: "var(--color-text-secondary)", borderColor: "var(--color-border)" } : {}}
                              >
                                {tag}
                              </button>
                            ))}
                          </div>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>Retention Category</label>
                            <select
                              value={uploadRetention}
                              onChange={(e) => setUploadRetention(e.target.value)}
                              className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                              style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                            >
                              {RETENTION_OPTIONS.map((opt) => (
                                <option key={opt.value} value={opt.value}>{opt.label}</option>
                              ))}
                            </select>
                          </div>
                          {uploadRetention === "CUSTOM" && (
                            <div>
                              <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>Custom Retention Date</label>
                              <input
                                type="date"
                                value={uploadCustomDate}
                                onChange={(e) => setUploadCustomDate(e.target.value)}
                                className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                                style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                              />
                            </div>
                          )}
                        </div>
                        <div className="flex gap-3">
                          <button onClick={() => handleUpload()} disabled={actionLoading || !uploadFile} className="btn-primary text-sm !py-2 !px-6">
                            {actionLoading ? "Uploading..." : "Upload"}
                          </button>
                          <button onClick={() => { setShowUpload(false); setUploadFile(null); }} className="text-sm px-4 py-2 rounded-lg border transition-colors" style={{ color: "var(--color-text-secondary)", borderColor: "var(--color-border)" }}>
                            Cancel
                          </button>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Drop zone */}
                  {selectedFolderId && !showUpload && (
                    <div
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                      onDrop={handleDrop}
                      className={`mb-6 p-6 rounded-lg border-2 border-dashed text-center transition-colors ${
                        dragging
                          ? "border-purple-500/60 bg-purple-500/10"
                          : ""
                      }`}
                      style={!dragging ? { borderColor: "var(--color-border)" } : {}}
                    >
                      <svg className="w-8 h-8 mx-auto mb-2" style={{ color: "var(--color-text-muted)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                      </svg>
                      <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                        Drop files here or{" "}
                        <button
                          onClick={() => { setShowUpload(true); setMessage(""); }}
                          className="text-purple-400 hover:text-purple-300 font-medium"
                        >
                          click to upload
                        </button>
                      </p>
                    </div>
                  )}

                  {/* File list */}
                  {folderFiles.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                        {selectedFolderId ? "No files in this folder yet." : "No files uploaded yet."}
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {folderFiles.map((file) => {
                        const retBadge = file.retention_category
                          ? RETENTION_BADGES[file.retention_category] || RETENTION_BADGES.CUSTOM
                          : null;
                        return (
                          <div
                            key={file.id}
                            className="p-4 rounded-lg border hover:border-purple-500/30 transition-colors flex flex-col md:flex-row justify-between items-start md:items-center gap-3"
                            style={{ borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" }}
                          >
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <svg className="w-4 h-4 shrink-0" style={{ color: "var(--color-text-muted)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                                </svg>
                                <h4 className="text-sm font-medium truncate">{file.original_filename || file.filename}</h4>
                              </div>
                              <div className="flex items-center gap-3 text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                                <span>{formatFileSize(file.size || 0)}</span>
                                <span>{new Date(file.uploaded_at).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}</span>
                                {retBadge && (
                                  <span className={`font-semibold px-1.5 py-0.5 rounded-full border ${retBadge.bg} ${retBadge.text}`} style={!retBadge.text ? { color: "var(--color-text-secondary)" } : {}}>
                                    {retBadge.label}
                                  </span>
                                )}
                              </div>
                              {file.tags && file.tags.length > 0 && (
                                <div className="flex gap-1.5 mt-1.5">
                                  {file.tags.map((tag) => (
                                    <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: "var(--color-bg-card)", color: "var(--color-text-secondary)" }}>
                                      {tag}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                            <button
                              onClick={() => handleDownload(file)}
                              className="text-xs font-bold text-purple-400 hover:text-purple-300 border border-purple-500/30 px-3 py-1.5 rounded-lg hover:bg-purple-500/10 transition-colors shrink-0"
                            >
                              Download
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Share Links Section */}
            {shareLinks.length > 0 && (
              <div className="glass-card p-6 mb-8 animate-fade-in-up" style={{ cursor: "default", animationDelay: "0.2s" }}>
                <h3 className="text-sm font-semibold uppercase tracking-wider mb-4" style={{ color: "var(--color-text-muted)" }}>
                  Share Links
                </h3>
                <div className="space-y-3">
                  {shareLinks.map((link) => (
                    <div
                      key={link.id}
                      className="p-4 rounded-lg border flex flex-col md:flex-row justify-between items-start md:items-center gap-3"
                      style={link.is_active ? { borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" } : { borderColor: "var(--color-border)", background: "var(--color-bg-secondary)", opacity: 0.6 }}
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="text-sm font-medium">{link.name}</h4>
                          <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full border ${
                            link.is_active
                              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                              : ""
                          }`} style={!link.is_active ? { background: "rgba(107, 114, 128, 0.1)", borderColor: "rgba(107, 114, 128, 0.3)", color: "var(--color-text-secondary)" } : {}}>
                            {link.is_active ? "ACTIVE" : "INACTIVE"}
                          </span>
                          {link.password_protected && (
                            <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: "var(--color-bg-card)", color: "var(--color-text-secondary)" }}>Password Protected</span>
                          )}
                        </div>
                        <div className="flex items-center gap-3 text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                          {link.expires_at && (
                            <span>Expires: {new Date(link.expires_at).toLocaleDateString("en-IN")}</span>
                          )}
                          <span>Downloads: {link.download_count}{link.max_downloads ? `/${link.max_downloads}` : ""}</span>
                        </div>
                      </div>
                      <button
                        onClick={() => copyToClipboard(link.url || `${window.location.origin}/share/${link.token}`)}
                        className="text-xs font-bold text-purple-400 hover:text-purple-300 border border-purple-500/30 px-3 py-1.5 rounded-lg hover:bg-purple-500/10 transition-colors shrink-0"
                      >
                        Copy Link
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Retention Alerts */}
            {retentionAlerts.length > 0 && (
              <div className="glass-card p-6 animate-fade-in-up" style={{ cursor: "default", animationDelay: "0.3s" }}>
                <h3 className="text-sm font-semibold uppercase tracking-wider mb-4" style={{ color: "var(--color-warning)" }}>
                  Retention Alerts
                </h3>
                <div className="space-y-3">
                  {retentionAlerts.map((alert) => {
                    const retBadge = RETENTION_BADGES[alert.retention_category] || RETENTION_BADGES.CUSTOM;
                    return (
                      <div
                        key={alert.file_id}
                        className="p-4 rounded-lg border border-amber-500/20 bg-amber-500/5 flex flex-col md:flex-row justify-between items-start md:items-center gap-3"
                      >
                        <div className="flex-1">
                          <h4 className="text-sm font-medium">{alert.filename}</h4>
                          <div className="flex items-center gap-3 mt-1 text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                            <span className={`font-semibold px-1.5 py-0.5 rounded-full border ${retBadge.bg} ${retBadge.text}`} style={!retBadge.text ? { color: "var(--color-text-secondary)" } : {}}>
                              {retBadge.label}
                            </span>
                            <span>Expires: {new Date(alert.expiry_date).toLocaleDateString("en-IN")}</span>
                          </div>
                        </div>
                        <span className="text-xs font-bold" style={{ color: alert.days_remaining <= 30 ? "var(--color-error)" : "var(--color-warning)" }}>
                          {alert.days_remaining} days remaining
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Retention Summary */}
            {retentionSummary && retentionSummary.categories && (
              <div className="glass-card p-6 mt-6 animate-fade-in-up" style={{ cursor: "default", animationDelay: "0.4s" }}>
                <h3 className="text-sm font-semibold uppercase tracking-wider mb-4" style={{ color: "var(--color-text-muted)" }}>
                  Retention Summary
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  {Object.entries(retentionSummary.categories as Record<string, number>).map(([cat, count]) => {
                    const badge = RETENTION_BADGES[cat] || RETENTION_BADGES.CUSTOM;
                    return (
                      <div key={cat} className="text-center p-3 rounded-lg border" style={{ borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" }}>
                        <p className={`text-lg font-bold ${badge.text}`} style={!badge.text ? { color: "var(--color-text-secondary)" } : {}}>{count as number}</p>
                        <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>{badge.label}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
