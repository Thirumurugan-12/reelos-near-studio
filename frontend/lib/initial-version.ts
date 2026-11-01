import type { Project } from "./api";

type InitialProject = Pick<Project, "current_version_id"> & {
  versions: { id: string }[];
  jobs: { version_id?: string }[];
};

export function initialVersion(project: InitialProject): string {
  const valid = new Set(project.versions.map((version) => version.id));
  return (
    [project.current_version_id, project.jobs[0]?.version_id].find(
      (id) => id && valid.has(id),
    ) || ""
  );
}
