import { useState } from "react";
import { uploadCsv, uploadImage } from "../api";

type Props = { onUploaded: (id: number) => void };

export default function UploadCard({ onUploaded }: Props) {
  const [mode, setMode] = useState<"photo" | "csv">("photo");
  const [file, setFile] = useState<File | null>(null);
  const [total, setTotal] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function run(task: () => Promise<number>) {
    setError("");
    setLoading(true);
    try {
      onUploaded(await task());
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  function submit() {
    if (!file) return;
    run(() => (mode === "photo" ? uploadImage(file) : uploadCsv(file, total)));
  }

  function trySample() {
    run(async () => {
      const blob = await (await fetch("/sample_bill.csv")).blob();
      const sample = new File([blob], "sample_bill.csv", { type: "text/csv" });
      return uploadCsv(sample, "3000.00");
    });
  }

  const disabled = !file || loading || (mode === "csv" && !total.trim());

  return (
    <div className="card">
      <h2>Check your medical bill</h2>
      <p className="muted">
        Upload your itemized bill. ClearBill points out charges worth asking about.
      </p>

      <div className="tabs">
        <button
          className={mode === "photo" ? "tab on" : "tab"}
          onClick={() => { setMode("photo"); setFile(null); }}
        >
          Photo of bill
        </button>
        <button
          className={mode === "csv" ? "tab on" : "tab"}
          onClick={() => { setMode("csv"); setFile(null); }}
        >
          CSV file
        </button>
      </div>

      <label>{mode === "photo" ? "Bill image (PNG or JPG)" : "Bill CSV"}</label>
      <input
        type="file"
        accept={mode === "photo" ? "image/png,image/jpeg" : ".csv,text/csv"}
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />

      {mode === "csv" && (
        <>
          <label>Total on the bill</label>
          <input
            value={total}
            onChange={(e) => setTotal(e.target.value)}
            placeholder="3000.00"
          />
        </>
      )}

      {error && <p className="error">{error}</p>}
      {loading && (
        <p className="muted">
          Reading your bill... the first photo can take a minute or two.
        </p>
      )}

      <div className="row">
        <button onClick={submit} disabled={disabled}>
          {loading ? "Working..." : "Check my bill"}
        </button>
        <button className="secondary" onClick={trySample} disabled={loading}>
          Try a sample bill
        </button>
      </div>
    </div>
  );
}