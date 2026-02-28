/**
 * Страница отчётов. Master + Admin.
 * GET /reports/personal, GET /reports/finance (только Admin).
 */
export default function ReportsPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Отчёты</h1>
      <p className="text-gray-500 mt-2">ИСЛАМ: блоки отчётов по персоналу и финансам.</p>
    </div>
  );
}
