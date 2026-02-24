interface FileUploadResponse {
  filename: string;
  content: string;
  size: number;
  type: string;
}

export const uploadTextFile = async (file: File): Promise<FileUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('/api/v1/rag/upload-text', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(error.detail || 'Failed to upload file');
  }

  return response.json();
};
