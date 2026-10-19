/** Decode any browser-recorded audio blob and re-encode it as 16-bit mono WAV (what the API expects). */
export async function toWav(blob: Blob): Promise<Blob> {
  const ctx = new AudioContext();
  try {
    const buffer = await ctx.decodeAudioData(await blob.arrayBuffer());
    const samples = buffer.getChannelData(0);
    const out = new DataView(new ArrayBuffer(44 + samples.length * 2));
    const str = (o: number, s: string) => [...s].forEach((c, i) => out.setUint8(o + i, c.charCodeAt(0)));

    str(0, "RIFF");
    out.setUint32(4, 36 + samples.length * 2, true);
    str(8, "WAVEfmt ");
    out.setUint32(16, 16, true);
    out.setUint16(20, 1, true); // PCM
    out.setUint16(22, 1, true); // mono
    out.setUint32(24, buffer.sampleRate, true);
    out.setUint32(28, buffer.sampleRate * 2, true);
    out.setUint16(32, 2, true);
    out.setUint16(34, 16, true);
    str(36, "data");
    out.setUint32(40, samples.length * 2, true);
    samples.forEach((s, i) => {
      const v = Math.max(-1, Math.min(1, s));
      out.setInt16(44 + i * 2, v < 0 ? v * 0x8000 : v * 0x7fff, true);
    });
    return new Blob([out], { type: "audio/wav" });
  } finally {
    void ctx.close();
  }
}
