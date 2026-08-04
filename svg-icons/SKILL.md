---
name: svg-icons
description: Browse the best SVG icon libraries and add beautiful icons to any project. Activated by /svg command.
---

# SVG Icons Skill — Добавление иконок в проект

Этот скилл активируется командой `/svg`. Он показывает лучшие библиотеки SVG иконок и помогает добавить их в любой проект.

---

## ШАГ 1 — Показать каталог библиотек

Когда пользователь пишет `/svg`, НЕМЕДЛЕННО покажи красивую таблицу со всеми библиотеками.

Запусти скрипт:

```bash
python3 ~/.gemini/skills/svg-icons/scripts/show_libraries.py
```

Он выведет отформатированный список библиотек с описанием, ссылками и командами установки.

---

## ШАГ 2 — Определить проект

После показа библиотек, **автоматически** определи тип проекта в текущей директории:

```bash
python3 ~/.gemini/skills/svg-icons/scripts/detect_project.py
```

Скрипт определяет:
- **React** → наличие `package.json` с react
- **Vue** → vue в зависимостях
- **Next.js** → next в зависимостях
- **Svelte** → svelte в зависимостях
- **Vanilla HTML** → наличие `.html` файлов
- **Django/Flask** → наличие `templates/` или `.py` файлов

---

## ШАГ 3 — Задать вопрос пользователю

Спроси:
1. Какую библиотеку выбрать (по номеру или названию)
2. Какие иконки нужны (или «добавь стандартный набор»)
3. В какой файл/компонент добавить

---

## ШАГ 4 — Установить и добавить иконки

### React / Next.js

```bash
# Lucide (рекомендуется)
npm install lucide-react

# Heroicons
npm install @heroicons/react

# Phosphor
npm install @phosphor-icons/react

# Tabler
npm install @tabler-icons-react

# Iconify (все 200,000 иконок сразу)
npm install @iconify/react
```

Добавить в компонент:
```jsx
// Lucide
import { Home, Search, Settings, Bell, User, Heart, Star } from 'lucide-react'

// Heroicons
import { HomeIcon, BellIcon, UserIcon } from '@heroicons/react/24/outline'

// Phosphor
import { House, Bell, User, Heart } from '@phosphor-icons/react'

// Iconify (любой набор)
import { Icon } from '@iconify/react'
// <Icon icon="lucide:home" />
// <Icon icon="ph:rocket" />
// <Icon icon="tabler:dashboard" />
// <Icon icon="heroicons:heart" />
```

### Vanilla HTML (CDN)

```html
<!-- Lucide -->
<script src="https://unpkg.com/lucide@latest"></script>
<i data-lucide="home"></i>
<script>lucide.createIcons();</script>

<!-- Heroicons (SVG inline) -->
<!-- Скопируй SVG код с https://heroicons.com -->

<!-- Ionicons -->
<script type="module" src="https://unpkg.com/ionicons@7.1.0/dist/ionicons/ionicons.esm.js"></script>
<ion-icon name="home"></ion-icon>

<!-- Iconify (CDN — все 200,000 иконок) -->
<script src="https://code.iconify.design/iconify-icon/2.1.0/iconify-icon.min.js"></script>
<iconify-icon icon="lucide:home"></iconify-icon>
<iconify-icon icon="ph:rocket"></iconify-icon>
```

### Vue / Nuxt

```bash
npm install @iconify/vue
# или
npm install lucide-vue-next
```

```vue
<script setup>
import { Icon } from '@iconify/vue'
import { Home } from 'lucide-vue-next'
</script>

<template>
  <Icon icon="ph:rocket" width="24" />
  <Home :size="24" />
</template>
```

### Svelte

```bash
npm install lucide-svelte
```

```svelte
<script>
  import { Home, Settings } from 'lucide-svelte';
</script>

<Home size={24} color="currentColor" />
```

---

## Каталог лучших библиотек

### 🥇 ТОП-10 библиотек SVG иконок

| # | Библиотека | Иконок | Стиль | Сайт |
|---|-----------|--------|-------|------|
| 1 | **Lucide** | 1,500+ | Тонкие, чистые | https://lucide.dev |
| 2 | **Phosphor Icons** | 9,000+ | 6 вариантов толщины | https://phosphoricons.com |
| 3 | **Heroicons** | 292+ | Outline + Solid | https://heroicons.com |
| 4 | **Tabler Icons** | 5,000+ | Чёткие, универсальные | https://tabler.io/icons |
| 5 | **Remix Icon** | 2,800+ | Line + Fill | https://remixicon.com |
| 6 | **Iconify** | 200,000+ | Все стили | https://iconify.design |
| 7 | **Material Symbols** | 3,000+ | Google Material | https://fonts.google.com/icons |
| 8 | **Radix Icons** | 300+ | Минималистичные | https://www.radix-ui.com/icons |
| 9 | **Feather Icons** | 287+ | Ультра-тонкие | https://feathericons.com |
| 10 | **Bootstrap Icons** | 2,000+ | Bootstrap стиль | https://icons.getbootstrap.com |

### 🎨 Специализированные

| Библиотека | Специализация | Сайт |
|-----------|--------------|------|
| **Simple Icons** | Логотипы брендов | https://simpleicons.org |
| **Devicons** | Языки программирования | https://devicon.dev |
| **Flag Icons** | Флаги стран | https://flagicons.lipis.dev |
| **Font Awesome** | Классика, огромная база | https://fontawesome.com |
| **Hugeicons** | Красивые, детализированные | https://hugeicons.com |

---

## Правила для AGY

1. **Всегда** показывай библиотеки с живыми ссылками — пользователь должен видеть красоту иконок
2. **Определи** стек проекта до установки — разные команды для React/Vue/HTML
3. **Рекомендуй** Lucide для React/Next.js, Phosphor для дизайн-систем, Heroicons для Tailwind
4. **Добавляй** иконки с правильными размерами и `currentColor` для поддержки темных тем
5. **Предложи** Iconify если пользователь хочет доступ ко всем библиотекам сразу
6. **Покажи живые примеры** кода сразу после установки — не просто `npm install`

---

## Пример хорошего ответа

Когда пользователь пишет `/svg`:

> «Вот лучшие библиотеки SVG иконок 🎨
>
> [таблица библиотек]
>
> Определил твой проект: **React + Next.js**
>
> Рекомендую **Lucide** — чистые иконки, идеальны для Next.js.
>
> Установить? Или выбери другую библиотеку из списка 👆»

После выбора:
> «Устанавливаю Lucide... ✅
>
> Вот иконки которые подойдут для твоего проекта:
> ```jsx
> import { Home, Search, Bell, User, Settings } from 'lucide-react'
> ```
> В какой компонент добавить?»
