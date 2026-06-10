"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import type { Branch } from "@/lib/auth/types";
import { listBranches } from "@/lib/core/api";
import {
  bulkCreateStockItems,
  createBranchTransfer,
  createCategory,
  createProduct,
  createStockItem,
  deleteCategory,
  deleteProduct,
  listBranchTransfers,
  listCategories,
  listProducts,
  listStockItems,
  listStockMovements,
  updateBranchTransferStatus,
  updateCategory,
  updateProduct,
  updateStockStatus,
} from "@/lib/inventory/api";
import type { BranchTransfer, Category, MovementType, Product, StockItem, StockMovement, StockStatus, TransferStatus } from "@/lib/inventory/types";

type Tab = "products" | "categories" | "stock" | "movements" | "transfers";

const stockStatuses: Array<{ value: StockStatus; label: string }> = [
  { value: "available", label: "موجود" },
  { value: "sold", label: "فروخته‌شده" },
  { value: "returned", label: "مرجوعی" },
  { value: "transferred", label: "در انتقال" },
  { value: "damaged", label: "آسیب‌دیده" },
];

const movementTypes: Array<{ value: MovementType; label: string }> = [
  { value: "purchase", label: "خرید / ورود" },
  { value: "sale", label: "فروش" },
  { value: "return", label: "مرجوعی" },
  { value: "transfer_out", label: "خروج انتقال" },
  { value: "transfer_in", label: "ورود انتقال" },
  { value: "adjustment", label: "اصلاح دستی" },
];

const transferStatuses: Array<{ value: TransferStatus; label: string }> = [
  { value: "pending", label: "در انتظار" },
  { value: "approved", label: "تأیید شده" },
  { value: "in_transit", label: "در مسیر" },
  { value: "completed", label: "تحویل شده" },
  { value: "cancelled", label: "لغو شده" },
];

const emptyCategoryForm = { name: "", parent: "", slug: "" };
const emptyProductForm = { name: "", category: "", barcode_prefix: "", buy_price: "0", sell_price: "0", description: "", is_active: true };
const emptyStockForm = { product: "", branch: "", barcode: "", serial_number: "", status: "available" as StockStatus };
const emptyTransferForm = { from_branch: "", to_branch: "", item_ids: "", notes: "" };

export function InventoryManager() {
  const [activeTab, setActiveTab] = useState<Tab>("products");
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [stockItems, setStockItems] = useState<StockItem[]>([]);
  const [movements, setMovements] = useState<StockMovement[]>([]);
  const [transfers, setTransfers] = useState<BranchTransfer[]>([]);
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [status, setStatus] = useState("");
  const [categoryForm, setCategoryForm] = useState(emptyCategoryForm);
  const [editingCategoryId, setEditingCategoryId] = useState<number | null>(null);
  const [productForm, setProductForm] = useState(emptyProductForm);
  const [editingProductId, setEditingProductId] = useState<number | null>(null);
  const [stockForm, setStockForm] = useState(emptyStockForm);
  const [bulkStockText, setBulkStockText] = useState("");
  const [transferForm, setTransferForm] = useState(emptyTransferForm);
  const [productFilters, setProductFilters] = useState({ search: "", category: "", branch: "", status: "" });
  const [movementFilters, setMovementFilters] = useState({ branch: "", type: "", date_from: "", date_to: "" });

  const selectedProduct = useMemo(() => products.find((product) => product.id === selectedProductId) ?? null, [products, selectedProductId]);

  async function loadBaseData() {
    const [categoryData, branchData] = await Promise.all([listCategories(), listBranches()]);
    setCategories(categoryData);
    setBranches(branchData);
  }

  async function loadProducts() {
    const data = await listProducts({
      search: productFilters.search || undefined,
      category: productFilters.category ? Number(productFilters.category) : undefined,
      branch: productFilters.branch ? Number(productFilters.branch) : undefined,
      status: productFilters.status ? (productFilters.status as StockStatus) : undefined,
    });
    setProducts(data);
    setSelectedProductId((current) => current ?? data[0]?.id ?? null);
  }

  async function loadStock(productId = selectedProductId) {
    const data = await listStockItems({ product: productId ?? undefined });
    setStockItems(data);
  }

  async function loadMovements() {
    const data = await listStockMovements({
      branch: movementFilters.branch ? Number(movementFilters.branch) : undefined,
      type: movementFilters.type || undefined,
      date_from: movementFilters.date_from || undefined,
      date_to: movementFilters.date_to || undefined,
    });
    setMovements(data);
  }

  async function loadTransfers() {
    setTransfers(await listBranchTransfers());
  }

  async function refreshAll() {
    await loadBaseData();
    await loadProducts();
    await loadStock();
    await loadMovements();
    await loadTransfers();
  }

  useEffect(() => {
    refreshAll().catch(() => setStatus("دریافت اطلاعات انبار ناموفق بود."));
  }, []);

  useEffect(() => {
    loadStock().catch(() => setStatus("دریافت موجودی محصول ناموفق بود."));
  }, [selectedProductId]);

  async function handleCategorySubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const input = { name: categoryForm.name, parent: categoryForm.parent ? Number(categoryForm.parent) : null, slug: categoryForm.slug || undefined };
    try {
      if (editingCategoryId) {
        await updateCategory(editingCategoryId, input);
        setStatus("دسته‌بندی ویرایش شد.");
      } else {
        await createCategory(input);
        setStatus("دسته‌بندی ایجاد شد.");
      }
      setCategoryForm(emptyCategoryForm);
      setEditingCategoryId(null);
      await loadBaseData();
    } catch {
      setStatus("ذخیره دسته‌بندی ناموفق بود.");
    }
  }

  async function handleProductSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const input = { ...productForm, category: Number(productForm.category) };
    try {
      if (editingProductId) {
        await updateProduct(editingProductId, input);
        setStatus("محصول ویرایش شد.");
      } else {
        await createProduct(input);
        setStatus("محصول ایجاد شد.");
      }
      setProductForm(emptyProductForm);
      setEditingProductId(null);
      await loadProducts();
    } catch {
      setStatus("ذخیره محصول ناموفق بود.");
    }
  }

  async function handleStockSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await createStockItem({ ...stockForm, product: Number(stockForm.product), branch: Number(stockForm.branch) });
      setStatus("موجودی تکی ثبت شد.");
      setStockForm(emptyStockForm);
      await loadStock();
      await loadProducts();
      await loadMovements();
    } catch {
      setStatus("ثبت موجودی تکی ناموفق بود.");
    }
  }

  async function handleBulkStockSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const items = bulkStockText
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => {
        const [barcode, serialNumber = ""] = line.split(",").map((part) => part.trim());
        return { barcode, serial_number: serialNumber };
      });
    if (!stockForm.product || !stockForm.branch || !items.length) {
      setStatus("برای افزودن دسته‌ای، محصول، شعبه و حداقل یک بارکد لازم است.");
      return;
    }
    try {
      await bulkCreateStockItems({ product: Number(stockForm.product), branch: Number(stockForm.branch), items, note: "Bulk stock entry from admin UI" });
      setStatus("موجودی دسته‌ای ثبت شد.");
      setBulkStockText("");
      await loadStock();
      await loadProducts();
      await loadMovements();
    } catch {
      setStatus("ثبت موجودی دسته‌ای ناموفق بود.");
    }
  }

  async function handleTransferSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const itemIds = transferForm.item_ids
      .split(",")
      .map((itemId) => Number(itemId.trim()))
      .filter(Boolean);
    try {
      await createBranchTransfer({ from_branch: Number(transferForm.from_branch), to_branch: Number(transferForm.to_branch), item_ids: itemIds, notes: transferForm.notes });
      setStatus("درخواست انتقال ایجاد شد.");
      setTransferForm(emptyTransferForm);
      await loadTransfers();
    } catch {
      setStatus("ایجاد درخواست انتقال ناموفق بود.");
    }
  }

  function startCategoryEdit(category: Category) {
    setEditingCategoryId(category.id);
    setCategoryForm({ name: category.name, parent: category.parent ? String(category.parent) : "", slug: category.slug });
    setActiveTab("categories");
  }

  function startProductEdit(product: Product) {
    setEditingProductId(product.id);
    setProductForm({
      name: product.name,
      category: String(product.category),
      barcode_prefix: product.barcode_prefix,
      buy_price: product.buy_price,
      sell_price: product.sell_price,
      description: product.description,
      is_active: product.is_active,
    });
    setActiveTab("products");
  }

  async function handleDeleteCategory(id: number) {
    try {
      await deleteCategory(id);
      setStatus("دسته‌بندی حذف شد.");
      await loadBaseData();
    } catch {
      setStatus("حذف دسته‌بندی ناموفق بود.");
    }
  }

  async function handleDeleteProduct(id: number) {
    try {
      await deleteProduct(id);
      setStatus("محصول حذف شد.");
      await loadProducts();
    } catch {
      setStatus("حذف محصول ناموفق بود.");
    }
  }

  async function handleStockStatusChange(stockItem: StockItem, nextStatus: StockStatus) {
    try {
      await updateStockStatus(stockItem.id, { status: nextStatus, note: "Status update from admin UI" });
      setStatus("وضعیت موجودی به‌روزرسانی شد.");
      await loadStock();
      await loadProducts();
      await loadMovements();
    } catch {
      setStatus("به‌روزرسانی وضعیت موجودی ناموفق بود.");
    }
  }

  async function handleTransferStatusChange(transfer: BranchTransfer, nextStatus: TransferStatus) {
    try {
      await updateBranchTransferStatus(transfer.id, { status: nextStatus, note: "Transfer status update from admin UI" });
      setStatus("وضعیت انتقال به‌روزرسانی شد.");
      await loadTransfers();
      await loadStock();
      await loadMovements();
    } catch {
      setStatus("به‌روزرسانی انتقال ناموفق بود.");
    }
  }

  return (
    <section className="space-y-5">
      <div className="flex flex-wrap gap-2">
        {[
          ["products", "محصولات"],
          ["categories", "دسته‌بندی‌ها"],
          ["stock", "موجودی‌ها"],
          ["movements", "گردش انبار"],
          ["transfers", "انتقال شعب"],
        ].map(([tab, label]) => (
          <button className={`rounded-2xl px-4 py-2 text-sm font-bold ${activeTab === tab ? "bg-white text-brand" : "border border-white/15 text-white/70"}`} key={tab} onClick={() => setActiveTab(tab as Tab)} type="button">
            {label}
          </button>
        ))}
      </div>
      {status ? <p className="rounded-2xl border border-white/10 bg-white/5 p-3 text-sm text-white/70">{status}</p> : null}
      {activeTab === "products" ? (
        <ProductsPanel
          branches={branches}
          categories={categories}
          filters={productFilters}
          form={productForm}
          onDelete={handleDeleteProduct}
          onEdit={startProductEdit}
          onFilterChange={setProductFilters}
          onFormChange={setProductForm}
          onReload={loadProducts}
          onSelectProduct={setSelectedProductId}
          onSubmit={handleProductSubmit}
          products={products}
          selectedProductId={selectedProductId}
          editingProductId={editingProductId}
        />
      ) : null}
      {activeTab === "categories" ? (
        <CategoriesPanel categories={categories} editingCategoryId={editingCategoryId} form={categoryForm} onDelete={handleDeleteCategory} onEdit={startCategoryEdit} onFormChange={setCategoryForm} onSubmit={handleCategorySubmit} />
      ) : null}
      {activeTab === "stock" ? (
        <StockPanel
          branches={branches}
          bulkStockText={bulkStockText}
          form={stockForm}
          onBulkSubmit={handleBulkStockSubmit}
          onBulkTextChange={setBulkStockText}
          onFormChange={setStockForm}
          onStatusChange={handleStockStatusChange}
          onSubmit={handleStockSubmit}
          products={products}
          selectedProduct={selectedProduct}
          stockItems={stockItems}
        />
      ) : null}
      {activeTab === "movements" ? <MovementsPanel filters={movementFilters} movements={movements} onFilterChange={setMovementFilters} onReload={loadMovements} branches={branches} /> : null}
      {activeTab === "transfers" ? (
        <TransfersPanel branches={branches} form={transferForm} onFormChange={setTransferForm} onStatusChange={handleTransferStatusChange} onSubmit={handleTransferSubmit} stockItems={stockItems} transfers={transfers} />
      ) : null}
    </section>
  );
}

function ProductsPanel({
  branches,
  categories,
  editingProductId,
  filters,
  form,
  onDelete,
  onEdit,
  onFilterChange,
  onFormChange,
  onReload,
  onSelectProduct,
  onSubmit,
  products,
  selectedProductId,
}: {
  branches: Branch[];
  categories: Category[];
  editingProductId: number | null;
  filters: { search: string; category: string; branch: string; status: string };
  form: typeof emptyProductForm;
  onDelete: (id: number) => void;
  onEdit: (product: Product) => void;
  onFilterChange: (filters: { search: string; category: string; branch: string; status: string }) => void;
  onFormChange: (form: typeof emptyProductForm) => void;
  onReload: () => void;
  onSelectProduct: (id: number) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  products: Product[];
  selectedProductId: number | null;
}) {
  return (
    <div className="space-y-5">
      <form className="grid gap-3 rounded-3xl border border-white/10 bg-white/5 p-5 md:grid-cols-2" onSubmit={onSubmit}>
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFormChange({ ...form, name: event.target.value })} placeholder="نام محصول" required value={form.name} />
        <select className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFormChange({ ...form, category: event.target.value })} required value={form.category}>
          <option value="">انتخاب دسته‌بندی</option>
          {categories.map((category) => (
            <option key={category.id} value={category.id}>{`${"— ".repeat(category.level - 1)}${category.name}`}</option>
          ))}
        </select>
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFormChange({ ...form, barcode_prefix: event.target.value })} placeholder="پیشوند بارکد" value={form.barcode_prefix} />
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" min="0" onChange={(event) => onFormChange({ ...form, buy_price: event.target.value })} placeholder="قیمت خرید" required type="number" value={form.buy_price} />
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" min="0" onChange={(event) => onFormChange({ ...form, sell_price: event.target.value })} placeholder="قیمت فروش" required type="number" value={form.sell_price} />
        <label className="flex items-center gap-2 text-sm text-white/70">
          <input checked={form.is_active} onChange={(event) => onFormChange({ ...form, is_active: event.target.checked })} type="checkbox" />
          فعال
        </label>
        <textarea className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none md:col-span-2" onChange={(event) => onFormChange({ ...form, description: event.target.value })} placeholder="توضیحات" value={form.description} />
        <button className="rounded-2xl bg-white px-5 py-3 font-black text-brand" type="submit">{editingProductId ? "ویرایش محصول" : "ایجاد محصول"}</button>
      </form>
      <div className="grid gap-3 rounded-3xl border border-white/10 bg-white/5 p-5 md:grid-cols-5">
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none md:col-span-2" onChange={(event) => onFilterChange({ ...filters, search: event.target.value })} placeholder="جستجوی محصول" value={filters.search} />
        <select className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFilterChange({ ...filters, category: event.target.value })} value={filters.category}>
          <option value="">همه دسته‌ها</option>
          {categories.map((category) => (
            <option key={category.id} value={category.id}>{category.name}</option>
          ))}
        </select>
        <select className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFilterChange({ ...filters, branch: event.target.value })} value={filters.branch}>
          <option value="">همه شعب</option>
          {branches.map((branch) => (
            <option key={branch.id} value={branch.id}>{branch.name}</option>
          ))}
        </select>
        <button className="rounded-2xl border border-white/15 px-4 py-3 font-bold" onClick={onReload} type="button">اعمال فیلتر</button>
      </div>
      <div className="grid gap-3">
        {products.map((product) => (
          <div className={`rounded-2xl border p-4 ${selectedProductId === product.id ? "border-white/40 bg-white/10" : "border-white/10 bg-white/5"}`} key={product.id}>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <button className="text-right" onClick={() => onSelectProduct(product.id)} type="button">
                <p className="font-black">{product.name}</p>
                <p className="mt-1 text-sm text-white/60">{product.category_name} — موجود: {product.available_count} / کل: {product.total_stock_count}</p>
              </button>
              <div className="flex flex-wrap gap-2 text-sm">
                <button className="rounded-xl border border-white/15 px-3 py-2" onClick={() => onEdit(product)} type="button">ویرایش</button>
                <button className="rounded-xl border border-red-300/40 px-3 py-2 text-red-100" onClick={() => onDelete(product.id)} type="button">حذف</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function CategoriesPanel({
  categories,
  editingCategoryId,
  form,
  onDelete,
  onEdit,
  onFormChange,
  onSubmit,
}: {
  categories: Category[];
  editingCategoryId: number | null;
  form: typeof emptyCategoryForm;
  onDelete: (id: number) => void;
  onEdit: (category: Category) => void;
  onFormChange: (form: typeof emptyCategoryForm) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <div className="space-y-5">
      <form className="grid gap-3 rounded-3xl border border-white/10 bg-white/5 p-5 md:grid-cols-3" onSubmit={onSubmit}>
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFormChange({ ...form, name: event.target.value })} placeholder="نام دسته‌بندی" required value={form.name} />
        <select className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFormChange({ ...form, parent: event.target.value })} value={form.parent}>
          <option value="">بدون والد</option>
          {categories.filter((category) => category.level < 3 && category.id !== editingCategoryId).map((category) => (
            <option key={category.id} value={category.id}>{`${"— ".repeat(category.level - 1)}${category.name}`}</option>
          ))}
        </select>
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFormChange({ ...form, slug: event.target.value })} placeholder="slug اختیاری" value={form.slug} />
        <button className="rounded-2xl bg-white px-5 py-3 font-black text-brand" type="submit">{editingCategoryId ? "ویرایش دسته‌بندی" : "ایجاد دسته‌بندی"}</button>
      </form>
      <div className="grid gap-3 md:grid-cols-2">
        {categories.map((category) => (
          <div className="flex items-center justify-between gap-3 rounded-2xl border border-white/10 bg-white/5 p-4" key={category.id}>
            <div>
              <p className="font-black">{`${"— ".repeat(category.level - 1)}${category.name}`}</p>
              <p className="text-sm text-white/60">سطح {category.level} — {category.children_count} زیرشاخه</p>
            </div>
            <div className="flex gap-2 text-sm">
              <button className="rounded-xl border border-white/15 px-3 py-2" onClick={() => onEdit(category)} type="button">ویرایش</button>
              <button className="rounded-xl border border-red-300/40 px-3 py-2 text-red-100" onClick={() => onDelete(category.id)} type="button">حذف</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function StockPanel({
  branches,
  bulkStockText,
  form,
  onBulkSubmit,
  onBulkTextChange,
  onFormChange,
  onStatusChange,
  onSubmit,
  products,
  selectedProduct,
  stockItems,
}: {
  branches: Branch[];
  bulkStockText: string;
  form: typeof emptyStockForm;
  onBulkSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onBulkTextChange: (value: string) => void;
  onFormChange: (form: typeof emptyStockForm) => void;
  onStatusChange: (stockItem: StockItem, status: StockStatus) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  products: Product[];
  selectedProduct: Product | null;
  stockItems: StockItem[];
}) {
  return (
    <div className="space-y-5">
      <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-white/70">
        محصول انتخاب‌شده: <span className="font-black text-white">{selectedProduct?.name ?? "از تب محصولات انتخاب کنید"}</span>
      </div>
      <form className="grid gap-3 rounded-3xl border border-white/10 bg-white/5 p-5 md:grid-cols-3" onSubmit={onSubmit}>
        <StockProductBranchFields branches={branches} form={form} onFormChange={onFormChange} products={products} />
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFormChange({ ...form, barcode: event.target.value })} placeholder="بارکد یونیک" required value={form.barcode} />
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFormChange({ ...form, serial_number: event.target.value })} placeholder="سریال" value={form.serial_number} />
        <select className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFormChange({ ...form, status: event.target.value as StockStatus })} value={form.status}>
          {stockStatuses.map((statusOption) => (
            <option key={statusOption.value} value={statusOption.value}>{statusOption.label}</option>
          ))}
        </select>
        <button className="rounded-2xl bg-white px-5 py-3 font-black text-brand" type="submit">ثبت موجودی تکی</button>
      </form>
      <form className="grid gap-3 rounded-3xl border border-white/10 bg-white/5 p-5" onSubmit={onBulkSubmit}>
        <textarea className="min-h-28 rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onBulkTextChange(event.target.value)} placeholder={"هر خط: barcode, serial\nمثال: DG-1001, SN-9"} value={bulkStockText} />
        <button className="rounded-2xl border border-white/15 px-5 py-3 font-bold" type="submit">افزودن دسته‌ای با محصول و شعبه انتخاب‌شده</button>
      </form>
      <div className="grid gap-3">
        {stockItems.map((stockItem) => (
          <div className="grid gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 md:grid-cols-[1fr_auto]" key={stockItem.id}>
            <div>
              <p className="font-black">{stockItem.barcode}</p>
              <p className="mt-1 text-sm text-white/60">{stockItem.product_name} — {stockItem.branch_name} — سریال: {stockItem.serial_number || "ندارد"}</p>
            </div>
            <select className="rounded-xl border border-white/15 bg-brand-dark px-3 py-2 text-sm" onChange={(event) => onStatusChange(stockItem, event.target.value as StockStatus)} value={stockItem.status}>
              {stockStatuses.map((statusOption) => (
                <option key={statusOption.value} value={statusOption.value}>{statusOption.label}</option>
              ))}
            </select>
          </div>
        ))}
      </div>
    </div>
  );
}

function StockProductBranchFields({ branches, form, onFormChange, products }: { branches: Branch[]; form: typeof emptyStockForm; onFormChange: (form: typeof emptyStockForm) => void; products: Product[] }) {
  return (
    <>
      <select className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFormChange({ ...form, product: event.target.value })} required value={form.product}>
        <option value="">انتخاب محصول</option>
        {products.map((product) => (
          <option key={product.id} value={product.id}>{product.name}</option>
        ))}
      </select>
      <select className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFormChange({ ...form, branch: event.target.value })} required value={form.branch}>
        <option value="">انتخاب شعبه</option>
        {branches.map((branch) => (
          <option key={branch.id} value={branch.id}>{branch.name}</option>
        ))}
      </select>
    </>
  );
}

function MovementsPanel({ branches, filters, movements, onFilterChange, onReload }: { branches: Branch[]; filters: { branch: string; type: string; date_from: string; date_to: string }; movements: StockMovement[]; onFilterChange: (filters: { branch: string; type: string; date_from: string; date_to: string }) => void; onReload: () => void }) {
  return (
    <div className="space-y-5">
      <div className="grid gap-3 rounded-3xl border border-white/10 bg-white/5 p-5 md:grid-cols-5">
        <select className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFilterChange({ ...filters, branch: event.target.value })} value={filters.branch}>
          <option value="">همه شعب</option>
          {branches.map((branch) => (
            <option key={branch.id} value={branch.id}>{branch.name}</option>
          ))}
        </select>
        <select className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFilterChange({ ...filters, type: event.target.value })} value={filters.type}>
          <option value="">همه عملیات‌ها</option>
          {movementTypes.map((movementType) => (
            <option key={movementType.value} value={movementType.value}>{movementType.label}</option>
          ))}
        </select>
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFilterChange({ ...filters, date_from: event.target.value })} type="date" value={filters.date_from} />
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFilterChange({ ...filters, date_to: event.target.value })} type="date" value={filters.date_to} />
        <button className="rounded-2xl border border-white/15 px-4 py-3 font-bold" onClick={onReload} type="button">اعمال فیلتر</button>
      </div>
      <div className="space-y-3">
        {movements.map((movement) => (
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4" key={movement.id}>
            <p className="font-black">{movement.product_name} — {movement.item_barcode}</p>
            <p className="mt-1 text-sm text-white/60">{movement.movement_type} از {movement.from_branch_name || "-"} به {movement.to_branch_name || "-"} — {new Date(movement.created_at).toLocaleString("fa-IR")}</p>
            {movement.note ? <p className="mt-2 text-sm text-white/70">{movement.note}</p> : null}
          </div>
        ))}
      </div>
    </div>
  );
}

function TransfersPanel({
  branches,
  form,
  onFormChange,
  onStatusChange,
  onSubmit,
  stockItems,
  transfers,
}: {
  branches: Branch[];
  form: typeof emptyTransferForm;
  onFormChange: (form: typeof emptyTransferForm) => void;
  onStatusChange: (transfer: BranchTransfer, status: TransferStatus) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  stockItems: StockItem[];
  transfers: BranchTransfer[];
}) {
  const availableItems = stockItems.filter((stockItem) => stockItem.status === "available");

  return (
    <div className="space-y-5">
      <form className="grid gap-3 rounded-3xl border border-white/10 bg-white/5 p-5 md:grid-cols-2" onSubmit={onSubmit}>
        <select className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFormChange({ ...form, from_branch: event.target.value })} required value={form.from_branch}>
          <option value="">شعبه مبدأ</option>
          {branches.map((branch) => (
            <option key={branch.id} value={branch.id}>{branch.name}</option>
          ))}
        </select>
        <select className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none" onChange={(event) => onFormChange({ ...form, to_branch: event.target.value })} required value={form.to_branch}>
          <option value="">شعبه مقصد</option>
          {branches.map((branch) => (
            <option key={branch.id} value={branch.id}>{branch.name}</option>
          ))}
        </select>
        <input className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none md:col-span-2" onChange={(event) => onFormChange({ ...form, item_ids: event.target.value })} placeholder="شناسه موجودی‌ها با کاما: 12,15,18" required value={form.item_ids} />
        <textarea className="rounded-2xl border border-white/15 bg-brand-dark px-4 py-3 outline-none md:col-span-2" onChange={(event) => onFormChange({ ...form, notes: event.target.value })} placeholder="یادداشت انتقال" value={form.notes} />
        <button className="rounded-2xl bg-white px-5 py-3 font-black text-brand" type="submit">ثبت درخواست انتقال</button>
      </form>
      <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-white/60">
        موجودی‌های قابل انتخاب در محصول فعلی: {availableItems.map((stockItem) => `${stockItem.id}:${stockItem.barcode}`).join("، ") || "موردی وجود ندارد"}
      </div>
      <div className="space-y-3">
        {transfers.map((transfer) => (
          <div className="grid gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 md:grid-cols-[1fr_auto]" key={transfer.id}>
            <div>
              <p className="font-black">{transfer.from_branch_name} ← {transfer.to_branch_name}</p>
              <p className="mt-1 text-sm text-white/60">{transfer.items.map((item) => item.barcode).join("، ")} — {new Date(transfer.created_at).toLocaleString("fa-IR")}</p>
              {transfer.notes ? <p className="mt-2 text-sm text-white/70">{transfer.notes}</p> : null}
            </div>
            <select className="rounded-xl border border-white/15 bg-brand-dark px-3 py-2 text-sm" onChange={(event) => onStatusChange(transfer, event.target.value as TransferStatus)} value={transfer.status}>
              {transferStatuses.map((transferStatus) => (
                <option key={transferStatus.value} value={transferStatus.value}>{transferStatus.label}</option>
              ))}
            </select>
          </div>
        ))}
      </div>
    </div>
  );
}
