---
name: svg-icons
description: Browse the best SVG icon libraries and add beautiful icons to any project. Smart auto-detection. Activated by /svg command.
---

# SVG Icons Skill — Умный подбор иконок для проекта

Активируется командой `/svg`. Анализирует проект и выдаёт **одну точную рекомендацию** — не список «попробуй это или то», а конкретно: установи вот это, вот так.

---

## ШАГ 1 — Показать каталог библиотек

```bash
python3 ~/.gemini/skills/svg-icons/scripts/show_libraries.py
```

Показывает красивую таблицу всех 10+ библиотек.

---

## ШАГ 2 — Умный анализ проекта

```bash
python3 ~/.gemini/skills/svg-icons/scripts/detect_project.py [путь]
```

Скрипт проводит **4-уровневый анализ** и выдаёт одну точную рекомендацию:

### Уровни приоритета (от высшего к низшему)

1. **UI-библиотека** — если в проекте уже есть shadcn/ui, MUI, Mantine и т.д., рекомендует иконки из той же экосистемы
2. **Система стилей** — Tailwind → Heroicons, styled-components → Lucide, UnoCSS → Iconify
3. **Тип продукта** — дашборд → Tabler, e-commerce → Phosphor, SaaS → Lucide, лендинг → Phosphor Thin
4. **Фреймворк** — Next.js/React → Lucide, Vue → Lucide Vue, Svelte → Lucide Svelte, Astro → Iconify

---

## ШАГ 3 — Что делать с результатом анализа

После запуска скрипта, **прочитай его вывод** и действуй так:

### Если уже установлены иконки
Скажи пользователю: «У тебя уже установлена [библиотека]. Просто скажи какие иконки нужны — добавлю.»

### Если рекомендация определена
1. Спроси: «Устанавливаю [НАЗВАНИЕ]? Это лучший выбор потому что [причина из скрипта].»
2. После подтверждения — **выполни команду установки из вывода скрипта**
3. Спроси: «Какие иконки нужны? Или добавить стандартный набор (home, search, menu, bell, user, settings)?»
4. Добавь иконки в нужный файл с **правильным кодом импорта и использования из вывода скрипта**

### Если тип проекта не определён
Спроси: «Что за проект? (дашборд / лендинг / SaaS / e-commerce / блог / портфолио)» — потом подбери по таблице ниже.

---

## Правила подбора (чтобы AGY понимал логику)

### По UI-библиотеке

| UI-библиотека | Иконки | Почему |
|---|---|---|
| shadcn/ui | `lucide-react` | shadcn использует Lucide нативно |
| Radix UI | `lucide-react` | Radix + Lucide — стандартная пара |
| MUI (Material UI) | `@mui/icons-material` | Родные MUI иконки, одинаковый стиль |
| Ant Design | `@ant-design/icons` | Ant иконки входят в экосистему antd |
| Mantine | `@tabler/icons-react` | Mantine официально рекомендует Tabler |
| Chakra UI | `@chakra-ui/icons` | Родные Chakra иконки |
| HeadlessUI | `@heroicons/react` | Создан командой Tailwind |
| DaisyUI | `lucide-react` | Нейтральные иконки не конфликтуют со стилями |
| Flowbite | `flowbite` | Flowbite Icons встроены в экосистему |
| PrimeVue | `primeicons` | Нативная библиотека PrimeFaces |
| Vuetify | `@mdi/js` | MDI — официальные иконки Vuetify |

### По системе стилей

| Стили | Иконки | Почему |
|---|---|---|
| Tailwind CSS | `@heroicons/react` | Созданы одной командой, одинаковый дизайн-язык |
| styled-components | `lucide-react` | Легко стилизуется через CSS props |
| Emotion | `lucide-react` | CSS-in-JS совместимость |
| UnoCSS | `@iconify/react` | Нативный пресет `@unocss/preset-icons` |

### По типу продукта

| Тип | Иконки | Почему |
|---|---|---|
| 📊 Dashboard / Admin | `@tabler/icons-react` | 5000+ иконок, созданы для data-heavy UI |
| 🛒 E-commerce | `@phosphor-icons/react` | Полный набор: cart, tag, receipt, delivery... |
| 💼 SaaS продукт | `lucide-react` | Linear, Vercel, Supabase — всё на Lucide |
| 🚀 Landing page | `@phosphor-icons/react` | Вариант `light`/`thin` даёт премиум-вайб |
| 📝 Блог / Docs | `lucide-react` | Docusaurus, VitePress, Nextra — Lucide |
| 🎨 Портфолио | `@phosphor-icons/react` | Элегантные thin-иконки |
| 💬 Чат / Мессенджер | `lucide-react` | Используют WhatsApp Web-клоны |
| ⚙️ Панель управления | `@tabler/icons-react` | Полный CRUD-набор |

### По фреймворку (fallback)

| Фреймворк | Пакет | Установка |
|---|---|---|
| Next.js | `lucide-react` | `npm install lucide-react` |
| React | `lucide-react` | `npm install lucide-react` |
| Vue 3 / Nuxt | `lucide-vue-next` | `npm install lucide-vue-next` |
| Svelte / SvelteKit | `lucide-svelte` | `npm install lucide-svelte` |
| Astro | `@iconify/react` | `npm install @iconify/react` |
| Angular | `@ng-icons/core` | `npm install @ng-icons/core` |
| Remix | `lucide-react` | `npm install lucide-react` |
| Gatsby | `lucide-react` | `npm install lucide-react` |
| Vanilla JS | `lucide` | `npm install lucide` |
| Vanilla HTML | CDN Lucide | `<script src="https://unpkg.com/lucide@latest">` |
| Django | Bootstrap Icons CDN | `<link href="cdn.jsdelivr.net/npm/bootstrap-icons...">` |
| Flask / FastAPI | Iconify CDN | `<script src="code.iconify.design/...">` |
| Rails | Heroicons gem | `gem "heroicons"` |

---

## Примеры добавления иконок

### lucide-react (React / Next.js)
```jsx
import { Home, Search, Bell, User, Settings, Heart, Star, ArrowRight, Menu, X, Plus, Trash2, Edit, Check, ChevronDown } from 'lucide-react'

// Использование:
<Home size={24} className="text-gray-600" />
<Bell size={20} strokeWidth={1.5} />
<ArrowRight size={16} color="currentColor" />

// В кнопке:
<button className="flex items-center gap-2">
  <Plus size={16} />
  Добавить
</button>
```

### @heroicons/react (Tailwind)
```jsx
import { HomeIcon, MagnifyingGlassIcon, BellIcon } from '@heroicons/react/24/outline'
import { HeartIcon, StarIcon } from '@heroicons/react/24/solid'

<HomeIcon className="h-6 w-6 text-gray-500" />
<BellIcon className="h-5 w-5" />
```

### @phosphor-icons/react (Phosphor)
```jsx
import { House, MagnifyingGlass, Bell, Rocket, Heart } from '@phosphor-icons/react'

<House size={24} />                          // regular
<Bell size={20} weight="light" />            // тонкая
<Rocket size={32} weight="duotone" />        // двухцветная
<Heart size={24} weight="fill" color="#ef4444" /> // заливка
```

### @tabler/icons-react (Tabler)
```jsx
import { IconHome, IconSearch, IconBell, IconDashboard, IconChartBar, IconUsers } from '@tabler/icons-react'

<IconHome size={24} stroke={1.5} />
<IconDashboard size={20} color="currentColor" />
```

### @iconify/react (универсальный)
```jsx
import { Icon } from '@iconify/react'

<Icon icon="lucide:home" width="24" />
<Icon icon="ph:rocket" width="24" />
<Icon icon="tabler:dashboard" width="24" />
<Icon icon="heroicons:heart" width="24" />
// Поиск иконок: https://icon-sets.iconify.design
```

### HTML CDN
```html
<!-- Lucide -->
<script src="https://unpkg.com/lucide@latest"></script>
<i data-lucide="home"></i>
<i data-lucide="search"></i>
<script>lucide.createIcons();</script>

<!-- Iconify (200K иконок) -->
<script src="https://code.iconify.design/iconify-icon/2.1.0/iconify-icon.min.js"></script>
<iconify-icon icon="lucide:home"></iconify-icon>
<iconify-icon icon="ph:rocket"></iconify-icon>
```

---

## Правила для AGY

1. **Всегда запускай оба скрипта** — сначала каталог, потом анализ проекта
2. **Давай одну рекомендацию** — не «попробуй это или то», а «установи вот это, вот почему»
3. **Объясняй почему** — используй причину из вывода скрипта
4. **Сразу показывай код** — не просто `npm install`, а полный рабочий пример
5. **Если просят конкретную иконку** — дай точное название для рекомендованной библиотеки
6. **Проверяй совместимость** — если уже есть иконки, не переустанавливай другую библиотеку

---

## Хороший пример ответа AGY

```
🎨 SVG Icon Libraries — 10 лучших библиотек

[таблица библиотек]

── Анализ проекта ──

⚡ Next.js  |  💎 shadcn/ui  |  📊 Dashboard

Рекомендую: lucide-react

💡 shadcn/ui использует Lucide нативно — идеальное совпадение стиля

Установка:
npm install lucide-react

Импорт:
import { Home, Search, Bell, User, Settings } from 'lucide-react'

Какие иконки нужны? Или добавить стандартный набор для дашборда?
```
