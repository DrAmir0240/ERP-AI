"use client";

import { FormEvent, useEffect, useState } from "react";

import {
  calculatePrice,
  createGame,
  createGameAccount,
  deleteGame,
  deleteGameAccount,
  listAccountSales,
  listGameAccounts,
  listGames,
  updateGame,
  updateGameAccount,
} from "@/lib/accounts/api";
import type { AccountSale, AccountType, Game, GameAccountListItem, GameInput, GamePlatform } from "@/lib/accounts/types";

type Tab = "accounts" | "games" | "sales" | "calculator";

const accountTypes: Array<{ value: AccountType; label: string }> = [
  { value: "ps_online", label: "PS آنلاین" },
  { value: "ps_offline", label: "PS آفلاین" },
  { value: "xbox", label: "Xbox" },
  { value: "nintendo", label: "Nintendo" },
];

const platformOptions: Array<{ value: GamePlatform; label: string }> = [
  { value: "ps", label: "PlayStation" },
  { value: "xbox", label: "Xbox" },
  { value: "nintendo", label: "Nintendo" },
];

const emptyAccountForm = {
  name: "",
  email: "",
  password: "",
  account_type: "ps_online" as AccountType,
  total_capacity: "0",
  notes: "",
  is_active: true,
  game_ids: [] as number[],
};

const emptyGameForm: GameInput = {
  name: "",
  platform: "ps",
  image_url: "",
  is_active: true,
};

export function AccountsManager() {
  const [activeTab, setActiveTab] = useState<Tab>("accounts");
  const [accounts, setAccounts] = useState<GameAccountListItem[]>([]);
  const [games, setGames] = useState<Game[]>([]);
  const [sales, setSales] = useState<AccountSale[]>([]);
  const [status, setStatus] = useState("");

  const [accountForm, setAccountForm] = useState(emptyAccountForm);
  const [editingAccountId, setEditingAccountId] = useState<number | null>(null);
  const [accountTypeFilter, setAccountTypeFilter] = useState<string>("");

  const [gameForm, setGameForm] = useState(emptyGameForm);
  const [editingGameId, setEditingGameId] = useState<number | null>(null);
  const [platformFilter, setPlatformFilter] = useState<string>("");

  const [salesAccountId, setSalesAccountId] = useState<string>("");

  const [calcGameIds, setCalcGameIds] = useState<number[]>([]);
  const [calcAccountType, setCalcAccountType] = useState<AccountType>("ps_online");
  const [calcResult, setCalcResult] = useState<{
    requested_games: Array<{ id: number; name: string }>;
    matching_accounts: Array<{ account_id: number; account_name: string; covered_game_ids: number[]; covered_count: number; total_capacity: number; sold_count: number }>;
    total_games_requested: number;
  } | null>(null);

  async function loadAccounts() {
    const params: Record<string, string> = {};
    if (accountTypeFilter) params.type = accountTypeFilter;
    const data = await listGameAccounts(params as { type?: AccountType });
    setAccounts(data);
  }

  async function loadGames() {
    const params: Record<string, string> = {};
    if (platformFilter) params.platform = platformFilter;
    const data = await listGames(params as { platform?: GamePlatform });
    setGames(data);
  }

  async function loadSales(accountId?: number) {
    if (accountId) {
      const data = await listAccountSales(accountId);
      setSales(data);
    } else {
      setSales([]);
    }
  }

  useEffect(() => {
    Promise.all([loadAccounts(), loadGames()]).catch(() => setStatus("دریافت اطلاعات اکانت ناموفق بود."));
  }, []);

  async function handleAccountSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const input = {
      name: accountForm.name,
      email: accountForm.email,
      password: accountForm.password,
      account_type: accountForm.account_type,
      total_capacity: Number(accountForm.total_capacity),
      notes: accountForm.notes,
      is_active: accountForm.is_active,
      game_ids: accountForm.game_ids,
    };
    try {
      if (editingAccountId) {
        await updateGameAccount(editingAccountId, input);
        setStatus("اکانت ویرایش شد.");
      } else {
        await createGameAccount(input);
        setStatus("اکانت ایجاد شد.");
      }
      setAccountForm(emptyAccountForm);
      setEditingAccountId(null);
      await loadAccounts();
    } catch {
      setStatus("ذخیره اکانت ناموفق بود.");
    }
  }

  function startAccountEdit(account: GameAccountListItem) {
    setAccountForm({
      name: account.name,
      email: account.email,
      password: "",
      account_type: account.account_type,
      total_capacity: String(account.total_capacity),
      notes: "",
      is_active: account.is_active,
      game_ids: [],
    });
    setEditingAccountId(account.id);
  }

  async function handleDeleteAccount(id: number) {
    try {
      await deleteGameAccount(id);
      setStatus("اکانت حذف شد.");
      await loadAccounts();
    } catch {
      setStatus("حذف اکانت ناموفق بود.");
    }
  }

  async function handleGameSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      if (editingGameId) {
        await updateGame(editingGameId, gameForm);
        setStatus("بازی ویرایش شد.");
      } else {
        await createGame(gameForm);
        setStatus("بازی ایجاد شد.");
      }
      setGameForm(emptyGameForm);
      setEditingGameId(null);
      await loadGames();
    } catch {
      setStatus("ذخیره بازی ناموفق بود.");
    }
  }

  function startGameEdit(game: Game) {
    setGameForm({
      name: game.name,
      platform: game.platform,
      image_url: game.image_url,
      is_active: game.is_active,
    });
    setEditingGameId(game.id);
  }

  async function handleDeleteGame(id: number) {
    try {
      await deleteGame(id);
      setStatus("بازی حذف شد.");
      await loadGames();
    } catch {
      setStatus("حذف بازی ناموفق بود.");
    }
  }

  async function handleSalesLoad() {
    if (salesAccountId) {
      try {
        await loadSales(Number(salesAccountId));
      } catch {
        setStatus("دریافت لاگ فروش ناموفق بود.");
      }
    }
  }

  async function handleCalculatePrice() {
    if (calcGameIds.length === 0) {
      setStatus("حداقل یک بازی انتخاب کنید.");
      return;
    }
    try {
      const result = await calculatePrice({ game_ids: calcGameIds, account_type: calcAccountType });
      setCalcResult(result);
      setStatus("");
    } catch {
      setStatus("محاسبه قیمت ناموفق بود.");
    }
  }

  function toggleCalcGame(gameId: number) {
    setCalcGameIds((prev) => (prev.includes(gameId) ? prev.filter((id) => id !== gameId) : [...prev, gameId]));
  }

  function toggleAccountGame(gameId: number) {
    setAccountForm((prev) => ({
      ...prev,
      game_ids: prev.game_ids.includes(gameId) ? prev.game_ids.filter((id) => id !== gameId) : [...prev.game_ids, gameId],
    }));
  }

  return (
    <section className="space-y-5">
      <div className="flex flex-wrap gap-2">
        {(
          [
            ["accounts", "اکانت‌ها"],
            ["games", "بازی‌ها"],
            ["sales", "لاگ فروش"],
            ["calculator", "محاسبه قیمت"],
          ] as const
        ).map(([tab, label]) => (
          <button className={`rounded-2xl px-4 py-2 text-sm font-bold ${activeTab === tab ? "bg-white text-brand" : "border border-white/15 text-white/70"}`} key={tab} onClick={() => setActiveTab(tab)} type="button">
            {label}
          </button>
        ))}
      </div>
      {status ? <p className="rounded-2xl border border-white/10 bg-white/5 p-3 text-sm text-white/70">{status}</p> : null}

      {activeTab === "accounts" ? (
        <AccountsPanel
          accounts={accounts}
          editingAccountId={editingAccountId}
          form={accountForm}
          games={games}
          onDelete={handleDeleteAccount}
          onEdit={startAccountEdit}
          onFilterChange={setAccountTypeFilter}
          onFormChange={setAccountForm}
          onReload={loadAccounts}
          onSubmit={handleAccountSubmit}
          onToggleGame={toggleAccountGame}
          typeFilter={accountTypeFilter}
        />
      ) : null}

      {activeTab === "games" ? (
        <GamesPanel
          editingGameId={editingGameId}
          form={gameForm}
          games={games}
          onDelete={handleDeleteGame}
          onEdit={startGameEdit}
          onFilterChange={setPlatformFilter}
          onFormChange={setGameForm}
          onReload={loadGames}
          onSubmit={handleGameSubmit}
          platformFilter={platformFilter}
        />
      ) : null}

      {activeTab === "sales" ? <SalesPanel accounts={accounts} onLoad={handleSalesLoad} onSelectAccount={setSalesAccountId} sales={sales} selectedAccountId={salesAccountId} /> : null}

      {activeTab === "calculator" ? (
        <CalculatorPanel calcAccountType={calcAccountType} calcGameIds={calcGameIds} games={games} onCalculate={handleCalculatePrice} onSetAccountType={setCalcAccountType} onToggleGame={toggleCalcGame} result={calcResult} />
      ) : null}
    </section>
  );
}

function AccountsPanel({
  accounts,
  editingAccountId,
  form,
  games,
  onDelete,
  onEdit,
  onFilterChange,
  onFormChange,
  onReload,
  onSubmit,
  onToggleGame,
  typeFilter,
}: {
  accounts: GameAccountListItem[];
  editingAccountId: number | null;
  form: typeof emptyAccountForm;
  games: Game[];
  onDelete: (id: number) => void;
  onEdit: (account: GameAccountListItem) => void;
  onFilterChange: (filter: string) => void;
  onFormChange: (form: typeof emptyAccountForm) => void;
  onReload: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onToggleGame: (gameId: number) => void;
  typeFilter: string;
}) {
  return (
    <div className="space-y-5">
      <form className="grid gap-3 rounded-3xl border border-white/10 bg-white/5 p-5 md:grid-cols-2" onSubmit={onSubmit}>
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(e) => onFormChange({ ...form, name: e.target.value })} placeholder="نام اکانت" required value={form.name} />
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(e) => onFormChange({ ...form, email: e.target.value })} placeholder="ایمیل" required type="email" value={form.email} />
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(e) => onFormChange({ ...form, password: e.target.value })} placeholder={editingAccountId ? "رمز جدید (اختیاری)" : "رمز عبور"} type="password" value={form.password} required={!editingAccountId} />
        <select className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(e) => onFormChange({ ...form, account_type: e.target.value as AccountType })} value={form.account_type}>
          {accountTypes.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(e) => onFormChange({ ...form, total_capacity: e.target.value })} placeholder="ظرفیت کل" type="number" min="0" value={form.total_capacity} />
        <textarea className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none md:col-span-2" onChange={(e) => onFormChange({ ...form, notes: e.target.value })} placeholder="یادداشت" rows={2} value={form.notes} />

        <div className="md:col-span-2">
          <p className="mb-2 text-sm text-white/60">بازی‌های اکانت:</p>
          <div className="flex flex-wrap gap-2 rounded-2xl border border-white/10 bg-brand-dark p-3 max-h-40 overflow-y-auto">
            {games.map((game) => (
              <button
                className={`rounded-xl px-3 py-1 text-xs font-bold ${form.game_ids.includes(game.id) ? "bg-white text-brand" : "border border-white/15 text-white/60"}`}
                key={game.id}
                onClick={() => onToggleGame(game.id)}
                type="button"
              >
                {game.name} ({game.platform_display})
              </button>
            ))}
            {games.length === 0 ? <span className="text-xs text-white/40">بازی‌ای ثبت نشده.</span> : null}
          </div>
        </div>

        <label className="flex items-center gap-2 text-sm text-white/70 md:col-span-2">
          <input checked={form.is_active} onChange={(e) => onFormChange({ ...form, is_active: e.target.checked })} type="checkbox" />
          فعال
        </label>
        <button className="rounded-2xl bg-white px-6 py-3 text-sm font-bold text-brand md:col-span-2" type="submit">
          {editingAccountId ? "ویرایش اکانت" : "افزودن اکانت"}
        </button>
      </form>

      <div className="flex items-center gap-3">
        <select className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-2 text-sm outline-none" onChange={(e) => onFilterChange(e.target.value)} value={typeFilter}>
          <option value="">همه انواع</option>
          {accountTypes.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
        <button className="rounded-2xl border border-white/15 px-4 py-2 text-sm text-white/70" onClick={onReload} type="button">
          بارگذاری
        </button>
      </div>

      <div className="overflow-x-auto rounded-3xl border border-white/10">
        <table className="w-full text-right text-sm">
          <thead className="border-b border-white/10 bg-white/5 text-white/60">
            <tr>
              <th className="px-4 py-3">نام</th>
              <th className="px-4 py-3">ایمیل</th>
              <th className="px-4 py-3">نوع</th>
              <th className="px-4 py-3">ظرفیت</th>
              <th className="px-4 py-3">فروش</th>
              <th className="px-4 py-3">بازی‌ها</th>
              <th className="px-4 py-3">وضعیت</th>
              <th className="px-4 py-3">عملیات</th>
            </tr>
          </thead>
          <tbody>
            {accounts.map((account) => (
              <tr className="border-b border-white/5 hover:bg-white/5" key={account.id}>
                <td className="px-4 py-3">{account.name}</td>
                <td className="px-4 py-3 text-xs">{account.email}</td>
                <td className="px-4 py-3">{account.account_type_display}</td>
                <td className="px-4 py-3">{account.total_capacity}</td>
                <td className="px-4 py-3">{account.sold_count}</td>
                <td className="px-4 py-3">{account.game_count}</td>
                <td className="px-4 py-3">{account.is_active ? "فعال" : "غیرفعال"}</td>
                <td className="flex gap-2 px-4 py-3">
                  <button className="text-xs text-white/60 hover:text-white" onClick={() => onEdit(account)} type="button">
                    ویرایش
                  </button>
                  <button className="text-xs text-red-400 hover:text-red-300" onClick={() => onDelete(account.id)} type="button">
                    حذف
                  </button>
                </td>
              </tr>
            ))}
            {accounts.length === 0 ? (
              <tr>
                <td className="px-4 py-6 text-center text-white/40" colSpan={8}>
                  اکانتی ثبت نشده.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function GamesPanel({
  editingGameId,
  form,
  games,
  onDelete,
  onEdit,
  onFilterChange,
  onFormChange,
  onReload,
  onSubmit,
  platformFilter,
}: {
  editingGameId: number | null;
  form: GameInput;
  games: Game[];
  onDelete: (id: number) => void;
  onEdit: (game: Game) => void;
  onFilterChange: (filter: string) => void;
  onFormChange: (form: GameInput) => void;
  onReload: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  platformFilter: string;
}) {
  return (
    <div className="space-y-5">
      <form className="grid gap-3 rounded-3xl border border-white/10 bg-white/5 p-5 md:grid-cols-2" onSubmit={onSubmit}>
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(e) => onFormChange({ ...form, name: e.target.value })} placeholder="نام بازی" required value={form.name} />
        <select className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(e) => onFormChange({ ...form, platform: e.target.value as GamePlatform })} value={form.platform}>
          {platformOptions.map((p) => (
            <option key={p.value} value={p.value}>
              {p.label}
            </option>
          ))}
        </select>
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(e) => onFormChange({ ...form, image_url: e.target.value })} placeholder="آدرس تصویر (URL)" value={form.image_url} />
        <label className="flex items-center gap-2 text-sm text-white/70">
          <input checked={form.is_active} onChange={(e) => onFormChange({ ...form, is_active: e.target.checked })} type="checkbox" />
          فعال
        </label>
        <button className="rounded-2xl bg-white px-6 py-3 text-sm font-bold text-brand md:col-span-2" type="submit">
          {editingGameId ? "ویرایش بازی" : "افزودن بازی"}
        </button>
      </form>

      <div className="flex items-center gap-3">
        <select className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-2 text-sm outline-none" onChange={(e) => onFilterChange(e.target.value)} value={platformFilter}>
          <option value="">همه پلتفرم‌ها</option>
          {platformOptions.map((p) => (
            <option key={p.value} value={p.value}>
              {p.label}
            </option>
          ))}
        </select>
        <button className="rounded-2xl border border-white/15 px-4 py-2 text-sm text-white/70" onClick={onReload} type="button">
          بارگذاری
        </button>
      </div>

      <div className="overflow-x-auto rounded-3xl border border-white/10">
        <table className="w-full text-right text-sm">
          <thead className="border-b border-white/10 bg-white/5 text-white/60">
            <tr>
              <th className="px-4 py-3">نام</th>
              <th className="px-4 py-3">پلتفرم</th>
              <th className="px-4 py-3">وضعیت</th>
              <th className="px-4 py-3">عملیات</th>
            </tr>
          </thead>
          <tbody>
            {games.map((game) => (
              <tr className="border-b border-white/5 hover:bg-white/5" key={game.id}>
                <td className="px-4 py-3">{game.name}</td>
                <td className="px-4 py-3">{game.platform_display}</td>
                <td className="px-4 py-3">{game.is_active ? "فعال" : "غیرفعال"}</td>
                <td className="flex gap-2 px-4 py-3">
                  <button className="text-xs text-white/60 hover:text-white" onClick={() => onEdit(game)} type="button">
                    ویرایش
                  </button>
                  <button className="text-xs text-red-400 hover:text-red-300" onClick={() => onDelete(game.id)} type="button">
                    حذف
                  </button>
                </td>
              </tr>
            ))}
            {games.length === 0 ? (
              <tr>
                <td className="px-4 py-6 text-center text-white/40" colSpan={4}>
                  بازی‌ای ثبت نشده.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SalesPanel({
  accounts,
  onLoad,
  onSelectAccount,
  sales,
  selectedAccountId,
}: {
  accounts: GameAccountListItem[];
  onLoad: () => void;
  onSelectAccount: (id: string) => void;
  sales: AccountSale[];
  selectedAccountId: string;
}) {
  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <select className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-2 text-sm outline-none" onChange={(e) => onSelectAccount(e.target.value)} value={selectedAccountId}>
          <option value="">انتخاب اکانت</option>
          {accounts.map((account) => (
            <option key={account.id} value={account.id}>
              {account.name} ({account.account_type_display})
            </option>
          ))}
        </select>
        <button className="rounded-2xl border border-white/15 px-4 py-2 text-sm text-white/70" onClick={onLoad} type="button">
          نمایش فروش‌ها
        </button>
      </div>

      <div className="overflow-x-auto rounded-3xl border border-white/10">
        <table className="w-full text-right text-sm">
          <thead className="border-b border-white/10 bg-white/5 text-white/60">
            <tr>
              <th className="px-4 py-3">اکانت</th>
              <th className="px-4 py-3">مشتری</th>
              <th className="px-4 py-3">تلفن</th>
              <th className="px-4 py-3">بازی‌های فروخته‌شده</th>
              <th className="px-4 py-3">شماره سفارش</th>
              <th className="px-4 py-3">تاریخ</th>
            </tr>
          </thead>
          <tbody>
            {sales.map((sale) => (
              <tr className="border-b border-white/5 hover:bg-white/5" key={sale.id}>
                <td className="px-4 py-3">{sale.account_name}</td>
                <td className="px-4 py-3">{sale.customer_name || "—"}</td>
                <td className="px-4 py-3 text-xs">{sale.customer_phone}</td>
                <td className="px-4 py-3 text-xs">
                  {sale.sold_games.map((g) => g.name).join("، ") || "—"}
                </td>
                <td className="px-4 py-3">{sale.order_id ?? "—"}</td>
                <td className="px-4 py-3 text-xs">{new Date(sale.sold_at).toLocaleDateString("fa-IR")}</td>
              </tr>
            ))}
            {sales.length === 0 ? (
              <tr>
                <td className="px-4 py-6 text-center text-white/40" colSpan={6}>
                  {selectedAccountId ? "فروشی ثبت نشده." : "اکانت انتخاب کنید."}
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function CalculatorPanel({
  calcAccountType,
  calcGameIds,
  games,
  onCalculate,
  onSetAccountType,
  onToggleGame,
  result,
}: {
  calcAccountType: AccountType;
  calcGameIds: number[];
  games: Game[];
  onCalculate: () => void;
  onSetAccountType: (type: AccountType) => void;
  onToggleGame: (gameId: number) => void;
  result: {
    requested_games: Array<{ id: number; name: string }>;
    matching_accounts: Array<{ account_id: number; account_name: string; covered_game_ids: number[]; covered_count: number; total_capacity: number; sold_count: number }>;
    total_games_requested: number;
  } | null;
}) {
  const psGames = games.filter((g) => g.platform === "ps");

  return (
    <div className="space-y-5">
      <div className="rounded-3xl border border-white/10 bg-white/5 p-5 space-y-4">
        <div className="flex items-center gap-3">
          <select className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-2 text-sm outline-none" onChange={(e) => onSetAccountType(e.target.value as AccountType)} value={calcAccountType}>
            <option value="ps_online">PS آنلاین</option>
            <option value="ps_offline">PS آفلاین</option>
          </select>
        </div>

        <div>
          <p className="mb-2 text-sm text-white/60">بازی‌ها را انتخاب کنید:</p>
          <div className="flex flex-wrap gap-2 rounded-2xl border border-white/10 bg-brand-dark p-3 max-h-52 overflow-y-auto">
            {psGames.map((game) => (
              <button
                className={`rounded-xl px-3 py-1 text-xs font-bold ${calcGameIds.includes(game.id) ? "bg-white text-brand" : "border border-white/15 text-white/60"}`}
                key={game.id}
                onClick={() => onToggleGame(game.id)}
                type="button"
              >
                {game.name}
              </button>
            ))}
            {psGames.length === 0 ? <span className="text-xs text-white/40">بازی PS ثبت نشده.</span> : null}
          </div>
        </div>

        <button className="rounded-2xl bg-white px-6 py-3 text-sm font-bold text-brand" onClick={onCalculate} type="button">
          محاسبه قیمت
        </button>
      </div>

      {result ? (
        <div className="space-y-4">
          <p className="text-sm text-white/70">
            {result.total_games_requested} بازی درخواست‌شده — {result.matching_accounts.length} اکانت مطابق
          </p>

          <div className="overflow-x-auto rounded-3xl border border-white/10">
            <table className="w-full text-right text-sm">
              <thead className="border-b border-white/10 bg-white/5 text-white/60">
                <tr>
                  <th className="px-4 py-3">اکانت</th>
                  <th className="px-4 py-3">بازی‌های موجود</th>
                  <th className="px-4 py-3">ظرفیت</th>
                  <th className="px-4 py-3">فروش‌ها</th>
                </tr>
              </thead>
              <tbody>
                {result.matching_accounts.map((account) => (
                  <tr className="border-b border-white/5 hover:bg-white/5" key={account.account_id}>
                    <td className="px-4 py-3">{account.account_name}</td>
                    <td className="px-4 py-3">
                      {account.covered_count} / {result.total_games_requested}
                    </td>
                    <td className="px-4 py-3">{account.total_capacity}</td>
                    <td className="px-4 py-3">{account.sold_count}</td>
                  </tr>
                ))}
                {result.matching_accounts.length === 0 ? (
                  <tr>
                    <td className="px-4 py-6 text-center text-white/40" colSpan={4}>
                      اکانت مطابقی یافت نشد.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </div>
  );
}
