export default function Notice() {
  return (
    <div className="notice">
      <p>
        ClearBill flags charges worth asking about. It isn't medical, legal, or
        financial advice.
      </p>
      <details>
        <summary>What ClearBill can and can't do</summary>
        <ul>
          <li>It works best on itemized bills with a code, date, and amount for each line.</li>
          <li>Photos are read by an AI model that can misread text, so double-check the results against your bill.</li>
          <li>It checks for duplicate charges, totals that don't add up, and a small set of bundled-service pairs. It doesn't check everything.</li>
          <li>A flag is a question to ask your billing office, not proof of an error.</li>
        </ul>
      </details>
    </div>
  );
}