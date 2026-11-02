import Notice from "./components/Notice";
import { useState } from "react";
import { getBill, type Bill } from "./api";
import BillResult from "./components/BillResult";
import UploadCard from "./components/UploadCard";

export default function App() {
  const [bill, setBill] = useState<Bill | null>(null);
  const [error, setError] = useState("");

  async function handleUploaded(id: number) {
    setError("");
    try {
      setBill(await getBill(id));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <>
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <div className="brand-mark">C</div>
            <h1 className="logo">ClearBill</h1>
          </div>
          <span className="badge">demo · synthetic data only</span>
        </div>
      </header>

      <main className="container">
        {!bill && (
          <section className="hero">
            <h2>Understand your medical bill.</h2>
            <p>Upload an itemized bill and see which charges are worth questioning.</p>
          </section>
        )}
        {error && <p className="error">{error}</p>}
        {bill ? (
          <BillResult bill={bill} onReset={() => setBill(null)} />
        ) : (
          <>
            <Notice />
            <UploadCard onUploaded={handleUploaded} />
          </>
        )}
      </main>
    </>
  );
}