"use client";

import { FormEvent, useEffect, useState } from "react";
import { SimpleCard } from "@/components/simple-card";

type Project = {
  id: number;
  name: string;
  description?: string | null;
};

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadProjects() {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE}/api/projects`, {
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error(`读取项目失败：HTTP ${response.status}`);
      }

      const data = await response.json();
      setProjects(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "读取项目失败");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!name.trim()) {
      setError("项目名称不能为空");
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      const response = await fetch(`${API_BASE}/api/projects`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: name.trim(),
          description: description.trim(),
        }),
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(`创建项目失败：HTTP ${response.status} ${message}`);
      }

      setName("");
      setDescription("");
      await loadProjects();
    } catch (err) {
      setError(err instanceof Error ? err.message : "创建项目失败");
    } finally {
      setSubmitting(false);
    }
  }

  useEffect(() => {
    loadProjects();
  }, []);

  return (
    <div className="space-y-6">
      <SimpleCard title="Projects 项目管理">
        <form onSubmit={handleCreateProject} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">项目名称</label>
            <input
              className="w-full rounded-lg border px-3 py-2"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="例如：第二血脉测试项目"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">项目描述</label>
            <textarea
              className="w-full rounded-lg border px-3 py-2"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="例如：影视漫剧生成中台MVP测试"
              rows={3}
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50"
          >
            {submitting ? "创建中..." : "新建项目"}
          </button>
        </form>
      </SimpleCard>

      <SimpleCard title="项目列表">
        {loading && <p>正在加载项目...</p>}

        {error && (
          <div className="rounded-lg border border-red-300 bg-red-50 p-3 text-red-700">
            {error}
          </div>
        )}

        {!loading && !error && projects.length === 0 && (
          <p className="text-gray-500">暂无项目，请创建第一个项目。</p>
        )}

        {!loading && !error && projects.length > 0 && (
          <div className="space-y-3">
            {projects.map((project) => (
              <div key={project.id} className="rounded-lg border p-4">
                <div className="text-sm text-gray-500">ID: {project.id}</div>
                <div className="text-lg font-semibold">{project.name}</div>
                <div className="mt-1 text-gray-700">
                  {project.description || "无描述"}
                </div>
              </div>
            ))}
          </div>
        )}
      </SimpleCard>
    </div>
  );
}