import { money, type Bill } from "../api";

const LABELS: Record<string, string> = {
  duplicate: "Possible duplicate charge",
  math_error: "Totals don't add up",
  unbundling: "Possibly billed twice (bundled service)",
};

type Props = { bill: Bill; onReset: () => void };

export default function BillResult({ bill, onReset }: Props) {
  const flagged = new Set(bill.flags.flatMap((f) => f.line_nos));
  const itemsTotal = bill.items.reduce((sum, i) => sum + i.amount_cents, 0);
  const atStake = bill.flags.reduce((sum, f) => sum + f.amount_at_stake_cents, 0);

  return (
    <>
      <div className="card">
        {bill.flags.length === 0 ? (
          <div className="summary good">
            No issues found by our checks. That doesn't guarantee the bill is
            correct.
          </div>
        ) : (
          <div className="summary warn">
            {bill.flags.length} thing{bill.flags.length > 1 ? "s" : ""} worth
            asking about, up to <strong>{money(atStake)}</strong> at stake
          </div>
        )}

        {bill.flags.map((f, i) => (
          <div key={i} className="flag">
            <div className="row spread">
              <strong>{LABELS[f.rule] ?? f.rule}</strong>
              <span>{money(f.amount_at_stake_cents)}</span>
            </div>
            <p>{f.message}</p>
            {f.line_nos.length > 0 && (
              <p className="muted small">
                Line{f.line_nos.length > 1 ? "s" : ""}: {f.line_nos.join(", ")}
              </p>
            )}
          </div>
        ))}
      </div>

      <div className="card">
        <h2>What we read from your bill</h2>
        <p className="muted small">
          Check these against your paper bill. If something was misread, the
          results above may be off.
        </p>
        <div className="scroll">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Date</th>
                <th>Code</th>
                <th>Description</th>
                <th className="right">Amount</th>
              </tr>
            </thead>
            <tbody>
              {bill.items.map((i) => (
                <tr key={i.line_no} className={flagged.has(i.line_no) ? "hit" : ""}>
                  <td>{i.line_no}</td>
                  <td>{i.service_date}</td>
                  <td>{i.code}</td>
                  <td>{i.description}</td>
                  <td className="right">{money(i.amount_cents)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="small">
          Total on bill: <strong>{money(bill.stated_total_cents)}</strong> · Lines
          add up to: <strong>{money(itemsTotal)}</strong>
        </p>
        <button onClick={onReset}>Check another bill</button>
      </div>

      <p className="muted small">
        ClearBill flags things worth asking about. It can't tell whether a
        charge is actually wrong, and it isn't medical or legal advice.
      </p>
    </>
  );
}