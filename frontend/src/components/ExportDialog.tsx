export function ExportDialog({ repositoryId }: { repositoryId: number }) {
  return <a href={`/api/repositories/${repositoryId}/export`}>Export</a>;
}
