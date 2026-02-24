export const transcribeAudio = async (blob: Blob): Promise<string> => {
  const formData = new FormData();
  formData.append("file", new File([blob], "recording.webm"));

  const response = await fetch("/api/v1/voice", {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    throw new Error("Voice transcription failed");
  }

  const data = await response.json();
  return data.text ?? "";
};
