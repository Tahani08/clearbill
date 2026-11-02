export type Item = {
  line_no: number;
  service_date: string;
  code: string;
  description: string;
  amount_cents: number;
};
export type Flag = {
  rule: string;
  line_nos: number[];
  message: string;
  amount_at_stake_cents: number;
};
export type Bill = {
  id: number;
  stated_total_cents: number;
  items: Item[];
  flags: Flag[];
};

async function parse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(
      typeof body?.detail === "string" ? body.detail : "Something went wrong"
    );
  }
  return res.json();
}

export async function uploadImage(file: File): Promise<number> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch("/api/bills/from-image", { method: "POST", body: form });
  return (await parse<{ id: number }>(res)).id;
}

export async function uploadCsv(file: File, total: string): Promise<number> {
  const form = new FormData();
  form.append("file", file);
  form.append("stated_total", total);
  const res = await fetch("/api/bills", { method: "POST", body: form });
  return (await parse<{ id: number }>(res)).id;
}

export async function getBill(id: number): Promise<Bill> {
  return parse<Bill>(await fetch(`/api/bills/${id}`));
}

export const money = (cents: number) =>
  (cents / 100).toLocaleString("en-US", { style: "currency", currency: "USD" });