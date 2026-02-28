/**
 * Страница пользователей. Только Admin.
 * POST /users/, PATCH /users/{id}, DELETE = деактивация (is_active=false).
 */
export default function UsersPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Пользователи</h1>
      <p className="text-gray-500 mt-2">ИСЛАМ: таблица, форма создания/редактирования. Кнопки «Редактировать», «Деактивировать».</p>
    </div>
  );
}
