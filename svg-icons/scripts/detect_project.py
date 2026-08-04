#!/usr/bin/env python3
"""
Smart Project Analyzer for SVG Icons Skill
Глубокий анализ проекта — стек, UI-библиотека, стиль, тип продукта.
Даёт единственную точную рекомендацию с объяснением почему.
"""

import json
import os
import sys
import re
from pathlib import Path

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
MAGENTA= "\033[95m"
BLUE   = "\033[94m"
WHITE  = "\033[97m"
RED    = "\033[91m"
ORANGE = "\033[38;5;214m"

# ── Базы данных рекомендаций ─────────────────────────────────────────────────

# UI-библиотека → иконки которые идут в пару
UI_LIB_ICONS = {
    "shadcn":         {"lib": "lucide-react",            "reason": "shadcn/ui использует Lucide — будет идеально совпадать"},
    "@radix-ui":      {"lib": "lucide-react",            "reason": "Radix UI и Lucide — стандартная пара в экосистеме"},
    "@mui":           {"lib": "@mui/icons-material",     "reason": "MUI Icons — родная библиотека для Material UI, одинаковый стиль"},
    "antd":           {"lib": "@ant-design/icons",       "reason": "Ant Design Icons входят в экосистему antd — идеальная совместимость"},
    "chakra-ui":      {"lib": "@chakra-ui/icons",        "reason": "Chakra иконки родные для Chakra UI, легко стилизовать через props"},
    "mantine":        {"lib": "@tabler/icons-react",     "reason": "Mantine рекомендует Tabler Icons — созданы одной командой"},
    "primevue":       {"lib": "primeicons",              "reason": "PrimeIcons — нативная библиотека для PrimeVue"},
    "vuetify":        {"lib": "@mdi/js",                 "reason": "Material Design Icons — официальный набор для Vuetify"},
    "quasar":         {"lib": "@quasar/extras",          "reason": "Quasar встроено поддерживает Ionicons, MDI, FA через extras"},
    "daisyui":        {"lib": "lucide-react",            "reason": "DaisyUI + Lucide — лёгкие, нейтральные иконки без лишнего стиля"},
    "flowbite":       {"lib": "flowbite",                "reason": "Flowbite Icons встроены в экосистему Flowbite"},
    "headlessui":     {"lib": "@heroicons/react",        "reason": "HeadlessUI создан командой Tailwind — Heroicons идеальная пара"},
}

# Стилизация → подходящие иконки
STYLING_ICONS = {
    "tailwindcss":        {"lib": "@heroicons/react",   "reason": "Heroicons созданы командой Tailwind — идеальная интеграция"},
    "styled-components":  {"lib": "lucide-react",       "reason": "Lucide легко стилизуется через styled-components с currentColor"},
    "@emotion":           {"lib": "lucide-react",       "reason": "Lucide совместим с CSS-in-JS библиотеками"},
    "unocss":             {"lib": "@iconify/react",     "reason": "UnoCSS + Iconify — нативная интеграция, пресет @unocss/preset-icons"},
    "windicss":           {"lib": "@heroicons/react",   "reason": "WindiCSS близок к Tailwind — Heroicons идеально вписываются"},
}

# Тип проекта → иконки (определяется по ключевым словам в package.json и файлах)
PROJECT_TYPE_ICONS = {
    "dashboard":   {"lib": "@tabler/icons-react",      "reason": "Tabler — 5000+ иконок, созданы специально для дашбордов и data-heavy UI"},
    "ecommerce":   {"lib": "@phosphor-icons/react",    "reason": "Phosphor — 9000+ иконок включают весь e-commerce набор (cart, tag, receipt...)"},
    "saas":        {"lib": "lucide-react",             "reason": "Lucide — стандарт для SaaS продуктов, используют Linear, Vercel, Supabase"},
    "blog":        {"lib": "lucide-react",             "reason": "Lucide — минималистичные иконки не отвлекают от контента"},
    "landing":     {"lib": "@phosphor-icons/react",    "reason": "Phosphor с вариантами thin/light даёт премиальный лендинг-вайб"},
    "mobile":      {"lib": "lucide-react",             "reason": "Lucide — SVG иконки на 24px сетке, идеальны для мобильных интерфейсов"},
    "admin":       {"lib": "@tabler/icons-react",      "reason": "Tabler создан для admin panel — есть всё: статус, таблицы, формы"},
    "chat":        {"lib": "lucide-react",             "reason": "Lucide использует WhatsApp Web, Slack-клоны — знакомые паттерны"},
    "portfolio":   {"lib": "@phosphor-icons/react",    "reason": "Phosphor Thin/Light — элегантные иконки для портфолио"},
    "docs":        {"lib": "lucide-react",             "reason": "Lucide — используют Docusaurus, VitePress, Nextra"},
}

# Фреймворк → базовая рекомендация (fallback)
FRAMEWORK_FALLBACK = {
    "nextjs":    {"lib": "lucide-react",            "npm": "lucide-react",            "reason": "Lucide — стандарт для Next.js экосистемы (Vercel, Linear, Supabase)"},
    "react":     {"lib": "lucide-react",            "npm": "lucide-react",            "reason": "Lucide — лучший выбор для React, 1500+ иконок, активная разработка"},
    "nuxt":      {"lib": "lucide-vue-next",         "npm": "lucide-vue-next",         "reason": "Lucide Vue — официальная Vue-версия Lucide"},
    "vue":       {"lib": "lucide-vue-next",         "npm": "lucide-vue-next",         "reason": "Lucide Vue Next — лучшая поддержка Vue 3 Composition API"},
    "svelte":    {"lib": "lucide-svelte",           "npm": "lucide-svelte",           "reason": "Lucide Svelte — официальная сборка, tree-shakeable"},
    "sveltekit": {"lib": "lucide-svelte",           "npm": "lucide-svelte",           "reason": "Lucide Svelte — работает с SvelteKit SSR без проблем"},
    "astro":     {"lib": "@iconify/react",          "npm": "@iconify/react",          "reason": "Iconify + Astro — доступ к 200K иконок, Islands Architecture совместимо"},
    "angular":   {"lib": "@ng-icons/core",          "npm": "@ng-icons/core",          "reason": "ng-icons — единая обёртка для всех иконок в Angular"},
    "remix":     {"lib": "lucide-react",            "npm": "lucide-react",            "reason": "Lucide — легко работает с Remix loader pattern"},
    "gatsby":    {"lib": "lucide-react",            "npm": "lucide-react",            "reason": "Lucide — tree-shaking работает отлично с Gatsby build"},
    "vanilla":   {"lib": "lucide",                  "npm": "lucide",                  "reason": "Lucide Vanilla — без зависимостей, работает в любом JS"},
    "html":      {"lib": "Lucide CDN",              "npm": None,                      "reason": "Lucide CDN — одна строка в HTML и все иконки готовы"},
    "django":    {"lib": "Bootstrap Icons",         "npm": None,                      "reason": "Bootstrap Icons — CDN, идеально для Django templates"},
    "flask":     {"lib": "Iconify CDN",             "npm": None,                      "reason": "Iconify CDN — все библиотеки доступны через data-атрибуты"},
    "fastapi":   {"lib": "Iconify CDN",             "npm": None,                      "reason": "Iconify CDN — если есть Jinja templates, проще некуда"},
    "laravel":   {"lib": "Blade UI Kit Icons",      "npm": None,                      "reason": "Blade UI Kit — SVG иконки нативно в Laravel Blade"},
    "rails":     {"lib": "Heroicons gem",           "npm": None,                      "reason": "heroicons gem — официальная Ruby-обёртка от Tailwind Labs"},
}

# Ключевые слова для определения типа продукта
PROJECT_TYPE_KEYWORDS = {
    "dashboard": ["dashboard", "analytics", "chart", "graph", "metric", "admin", "recharts", "chart.js", "apexcharts", "d3", "victory", "nivo"],
    "ecommerce": ["cart", "shop", "store", "product", "checkout", "stripe", "payment", "commerce", "shopify", "woocommerce", "snipcart"],
    "saas":      ["subscription", "billing", "tenant", "workspace", "team", "organization", "plan", "pricing", "stripe", "paddle"],
    "blog":      ["blog", "post", "article", "content", "cms", "markdown", "mdx", "contentful", "sanity", "ghost"],
    "landing":   ["landing", "hero", "features", "testimonial", "pricing", "cta", "framer", "gsap", "animejs"],
    "mobile":    ["react-native", "expo", "capacitor", "ionic", "cordova", "nativescript"],
    "admin":     ["admin", "crud", "table", "form", "filter", "pagination", "tanstack", "react-table", "ag-grid"],
    "chat":      ["chat", "message", "socket", "socket.io", "pusher", "ably", "realtime", "stream", "sendbird"],
    "portfolio": ["portfolio", "resume", "cv", "personal", "showcase", "project"],
    "docs":      ["docs", "documentation", "nextra", "docusaurus", "vitepress", "gitbook"],
}


def read_file_safe(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


def scan_source_files(path, extensions=(".ts", ".tsx", ".js", ".jsx", ".vue", ".svelte")):
    """Читает исходники для поиска ключевых слов."""
    content = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".git", ".next", "dist", "build", ".nuxt", ".svelte-kit")]
        for f in files:
            if any(f.endswith(ext) for ext in extensions):
                content.append(read_file_safe(os.path.join(root, f)))
                if len(content) > 50:  # читаем максимум 50 файлов
                    return "\n".join(content)
    return "\n".join(content)


def detect_framework(deps, path):
    """Определяет фреймворк."""
    dep_str = " ".join(deps.keys()).lower()

    if "next" in deps:
        return "nextjs"
    if "@sveltejs/kit" in deps:
        return "sveltekit"
    if "svelte" in dep_str:
        return "svelte"
    if "nuxt" in deps:
        return "nuxt"
    if "vue" in dep_str:
        return "vue"
    if "@remix-run/react" in deps or "remix" in dep_str:
        return "remix"
    if "gatsby" in dep_str:
        return "gatsby"
    if "astro" in dep_str:
        return "astro"
    if "@angular/core" in deps:
        return "angular"
    if "react" in dep_str:
        return "react"
    if "expo" in deps or "react-native" in deps:
        return "mobile"

    # Python
    if os.path.exists(os.path.join(path, "manage.py")):
        return "django"
    if os.path.exists(os.path.join(path, "app.py")):
        return "flask"
    if os.path.exists(os.path.join(path, "main.py")):
        req = read_file_safe(os.path.join(path, "requirements.txt"))
        if "fastapi" in req.lower():
            return "fastapi"
        return "flask"

    # HTML
    html_files = list(Path(path).glob("*.html"))
    if html_files:
        return "html"

    if os.path.exists(os.path.join(path, "Gemfile")):
        return "rails"

    return "vanilla"


def detect_ui_library(deps):
    """Определяет UI-библиотеку."""
    dep_str = " ".join(deps.keys()).lower()
    for ui, data in UI_LIB_ICONS.items():
        if ui.lower() in dep_str:
            return ui, data
    return None, None


def detect_styling(deps):
    """Определяет систему стилей."""
    dep_str = " ".join(deps.keys()).lower()
    for style, data in STYLING_ICONS.items():
        if style.lower() in dep_str:
            return style, data
    return None, None


def detect_project_type(deps, source_code):
    """Определяет тип продукта по зависимостям и исходникам."""
    dep_str = " ".join(deps.keys()).lower()
    combined = dep_str + "\n" + source_code.lower()

    scores = {}
    for ptype, keywords in PROJECT_TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in combined)
        if score > 0:
            scores[ptype] = score

    if scores:
        return max(scores, key=scores.get)
    return None


def check_existing_icons(deps):
    """Проверяет — уже установлены какие-то иконки."""
    icon_packages = {
        "lucide-react": "Lucide",
        "lucide-vue-next": "Lucide Vue",
        "lucide-svelte": "Lucide Svelte",
        "@heroicons/react": "Heroicons",
        "@phosphor-icons/react": "Phosphor",
        "@tabler/icons-react": "Tabler",
        "@tabler-icons-react": "Tabler",
        "@iconify/react": "Iconify",
        "remixicon": "Remix Icon",
        "@radix-ui/react-icons": "Radix Icons",
        "react-icons": "React Icons",
        "@mui/icons-material": "Material Icons",
        "@ant-design/icons": "Ant Icons",
        "@fortawesome/react-fontawesome": "Font Awesome",
        "bootstrap-icons": "Bootstrap Icons",
        "hugeicons-react": "Hugeicons",
    }
    found = []
    for pkg, name in icon_packages.items():
        if pkg in deps:
            found.append({"package": pkg, "name": name})
    return found


def get_pm(path):
    if os.path.exists(os.path.join(path, "pnpm-lock.yaml")):
        return "pnpm"
    if os.path.exists(os.path.join(path, "yarn.lock")):
        return "yarn"
    if os.path.exists(os.path.join(path, "bun.lockb")):
        return "bun"
    return "npm"


def get_install_cmd(pm, pkg):
    if pkg is None:
        return None
    cmds = {"npm": f"npm install {pkg}", "pnpm": f"pnpm add {pkg}", "yarn": f"yarn add {pkg}", "bun": f"bun add {pkg}"}
    return cmds.get(pm, f"npm install {pkg}")


USAGE_EXAMPLES = {
    "lucide-react": {
        "import": "import {{ Home, Search, Bell, User, Settings, Heart, Star, ArrowRight, Menu, X }} from 'lucide-react'",
        "usage": "<Home size={{24}} className=\"text-gray-600\" />\n<Bell size={{20}} strokeWidth={{1.5}} />\n<ArrowRight size={{16}} color=\"currentColor\" />",
    },
    "lucide-vue-next": {
        "import": "import {{ Home, Search, Bell, User, Settings }} from 'lucide-vue-next'",
        "usage": "<Home :size=\"24\" />\n<Bell :size=\"20\" :stroke-width=\"1.5\" />",
    },
    "lucide-svelte": {
        "import": "import {{ Home, Search, Bell }} from 'lucide-svelte'",
        "usage": "<Home size={{24}} />\n<Bell size={{20}} strokeWidth={{1.5}} />",
    },
    "@heroicons/react": {
        "import": "import {{ HomeIcon, MagnifyingGlassIcon, BellIcon, UserIcon }} from '@heroicons/react/24/outline'\nimport {{ HeartIcon, StarIcon }} from '@heroicons/react/24/solid'",
        "usage": "<HomeIcon className=\"h-6 w-6 text-gray-500\" />\n<BellIcon className=\"h-5 w-5\" />",
    },
    "@phosphor-icons/react": {
        "import": "import {{ House, MagnifyingGlass, Bell, User, Rocket, Heart }} from '@phosphor-icons/react'",
        "usage": "<House size={{24}} />\n<Bell size={{20}} weight=\"light\" />\n<Rocket size={{32}} weight=\"duotone\" color=\"#6366f1\" />",
    },
    "@tabler/icons-react": {
        "import": "import {{ IconHome, IconSearch, IconBell, IconUser, IconDashboard, IconChartBar }} from '@tabler/icons-react'",
        "usage": "<IconHome size={{24}} stroke={{1.5}} />\n<IconDashboard size={{20}} color=\"currentColor\" />",
    },
    "@iconify/react": {
        "import": "import {{ Icon }} from '@iconify/react'",
        "usage": "<Icon icon=\"lucide:home\" width=\"24\" />\n<Icon icon=\"ph:rocket\" width=\"24\" />\n<Icon icon=\"tabler:dashboard\" width=\"24\" />\n<Icon icon=\"heroicons:heart\" width=\"24\" />",
    },
    "@mui/icons-material": {
        "import": "import Home from '@mui/icons-material/Home'\nimport Search from '@mui/icons-material/Search'\nimport Notifications from '@mui/icons-material/Notifications'",
        "usage": "<Home sx={{ fontSize: 24 }} />\n<Notifications color=\"primary\" />",
    },
    "@ant-design/icons": {
        "import": "import {{ HomeOutlined, SearchOutlined, BellOutlined, UserOutlined }} from '@ant-design/icons'",
        "usage": "<HomeOutlined style={{ fontSize: '24px' }} />\n<BellOutlined />",
    },
}

CDN_EXAMPLES = {
    "Lucide CDN": {
        "html": '<script src="https://unpkg.com/lucide@latest"></script>\n\n<!-- Добавь иконки: -->\n<i data-lucide="home"></i>\n<i data-lucide="search"></i>\n<i data-lucide="bell"></i>\n\n<!-- Активируй: -->\n<script>lucide.createIcons();</script>',
    },
    "Bootstrap Icons": {
        "html": '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">\n\n<!-- Используй: -->\n<i class="bi bi-house"></i>\n<i class="bi bi-search"></i>\n<i class="bi bi-bell"></i>',
    },
    "Iconify CDN": {
        "html": '<script src="https://code.iconify.design/iconify-icon/2.1.0/iconify-icon.min.js"></script>\n\n<!-- Любые иконки из 200K: -->\n<iconify-icon icon="lucide:home"></iconify-icon>\n<iconify-icon icon="ph:rocket"></iconify-icon>\n<iconify-icon icon="tabler:dashboard"></iconify-icon>',
    },
}


def analyze(path="."):
    path = os.path.abspath(path)
    result = {"path": path, "framework": None, "ui_library": None, "styling": None,
              "project_type": None, "existing_icons": [], "recommendation": None,
              "reasoning_chain": [], "install_command": None, "import_example": None, "usage_example": None}

    # Читаем package.json
    pkg_path = os.path.join(path, "package.json")
    deps = {}
    pkg_name = ""
    pkg_description = ""
    if os.path.exists(pkg_path):
        try:
            pkg = json.loads(read_file_safe(pkg_path))
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            pkg_name = pkg.get("name", "")
            pkg_description = pkg.get("description", "")
        except Exception:
            pass

    pm = get_pm(path)
    result["package_manager"] = pm

    # ── Шаг 1: Определяем фреймворк ─────────────────────────────────────────
    framework = detect_framework(deps, path)
    result["framework"] = framework
    fw_data = FRAMEWORK_FALLBACK.get(framework, FRAMEWORK_FALLBACK["vanilla"])
    result["reasoning_chain"].append(f"Фреймворк: {framework}")

    # ── Шаг 2: Проверяем уже установленные иконки ───────────────────────────
    existing = check_existing_icons(deps)
    result["existing_icons"] = existing
    if existing:
        result["reasoning_chain"].append(f"Уже установлены: {', '.join(e['name'] for e in existing)}")

    # ── Шаг 3: Анализируем исходники ────────────────────────────────────────
    source_code = ""
    if framework not in ("django", "flask", "fastapi", "rails", "html"):
        source_code = scan_source_files(path)

    # ── Шаг 4: UI-библиотека (самый высокий приоритет) ──────────────────────
    ui_key, ui_data = detect_ui_library(deps)
    if ui_key:
        result["ui_library"] = ui_key
        result["reasoning_chain"].append(f"UI-библиотека: {ui_key} → рекомендует {ui_data['lib']}")
        result["recommendation"] = ui_data["lib"]
        result["recommendation_reason"] = ui_data["reason"]
        result["recommendation_priority"] = "UI_LIBRARY"

    # ── Шаг 5: Стилизация (второй приоритет) ────────────────────────────────
    if not result["recommendation"]:
        style_key, style_data = detect_styling(deps)
        if style_key:
            result["styling"] = style_key
            result["reasoning_chain"].append(f"Стилизация: {style_key} → рекомендует {style_data['lib']}")
            result["recommendation"] = style_data["lib"]
            result["recommendation_reason"] = style_data["reason"]
            result["recommendation_priority"] = "STYLING"

    # ── Шаг 6: Тип продукта (третий приоритет) ──────────────────────────────
    if not result["recommendation"]:
        search_text = pkg_name + " " + pkg_description + " " + source_code
        ptype = detect_project_type(deps, search_text)
        if ptype:
            result["project_type"] = ptype
            ptype_data = PROJECT_TYPE_ICONS.get(ptype, {})
            result["reasoning_chain"].append(f"Тип продукта: {ptype} → рекомендует {ptype_data.get('lib', '')}")
            result["recommendation"] = ptype_data.get("lib")
            result["recommendation_reason"] = ptype_data.get("reason", "")
            result["recommendation_priority"] = "PROJECT_TYPE"

    # ── Шаг 7: Фреймворк-фоллбэк ────────────────────────────────────────────
    if not result["recommendation"]:
        result["recommendation"] = fw_data["lib"]
        result["recommendation_reason"] = fw_data["reason"]
        result["recommendation_priority"] = "FRAMEWORK"
        result["reasoning_chain"].append(f"Fallback по фреймворку → {fw_data['lib']}")

    # ── Шаг 8: npm-пакет и примеры ──────────────────────────────────────────
    rec = result["recommendation"]
    npm_pkg = fw_data.get("npm") if result.get("recommendation_priority") == "FRAMEWORK" else rec.replace(" ", "").lower()

    # Маппинг человекочитаемых имён → npm пакеты
    friendly_to_npm = {
        "lucide-react": "lucide-react",
        "@heroicons/react": "@heroicons/react",
        "@phosphor-icons/react": "@phosphor-icons/react",
        "@tabler/icons-react": "@tabler/icons-react",
        "@iconify/react": "@iconify/react",
        "@mui/icons-material": "@mui/icons-material",
        "@ant-design/icons": "@ant-design/icons",
        "@chakra-ui/icons": "@chakra-ui/icons",
        "@tabler-icons-react": "@tabler/icons-react",
        "lucide-vue-next": "lucide-vue-next",
        "lucide-svelte": "lucide-svelte",
        "@radix-ui/react-icons": "@radix-ui/react-icons",
        "lucide": "lucide",
        "primeicons": "primeicons",
        "@mdi/js": "@mdi/js",
        "hugeicons-react": "hugeicons-react",
    }

    npm_pkg = friendly_to_npm.get(rec)
    result["npm_package"] = npm_pkg
    result["install_command"] = get_install_cmd(pm, npm_pkg) if npm_pkg else None

    if rec in USAGE_EXAMPLES:
        result["import_example"] = USAGE_EXAMPLES[rec]["import"]
        result["usage_example"] = USAGE_EXAMPLES[rec]["usage"]
    elif rec in CDN_EXAMPLES:
        result["cdn_example"] = CDN_EXAMPLES[rec]["html"]

    return result


# ── Красивый вывод ──────────────────────────────────────────────────────────

FW_LABELS = {
    "nextjs": ("⚡", "Next.js"),
    "react": ("⚛️ ", "React"),
    "vue": ("💚", "Vue 3"),
    "nuxt": ("💚", "Nuxt 3"),
    "svelte": ("🔥", "Svelte"),
    "sveltekit": ("🔥", "SvelteKit"),
    "astro": ("🚀", "Astro"),
    "angular": ("🔴", "Angular"),
    "remix": ("🎵", "Remix"),
    "gatsby": ("⚡", "Gatsby"),
    "mobile": ("📱", "React Native / Expo"),
    "vanilla": ("⚡", "Vanilla JS"),
    "html": ("🌐", "Vanilla HTML"),
    "django": ("🐍", "Django"),
    "flask": ("🐍", "Flask"),
    "fastapi": ("🐍", "FastAPI"),
    "rails": ("💎", "Ruby on Rails"),
}

PRIORITY_LABELS = {
    "UI_LIBRARY":   (GREEN,   "UI-библиотека"),
    "STYLING":      (CYAN,    "Система стилей"),
    "PROJECT_TYPE": (MAGENTA, "Тип продукта"),
    "FRAMEWORK":    (YELLOW,  "Фреймворк"),
}

PTYPE_EMOJI = {
    "dashboard": "📊",
    "ecommerce": "🛒",
    "saas":      "💼",
    "blog":      "📝",
    "landing":   "🚀",
    "mobile":    "📱",
    "admin":     "⚙️ ",
    "chat":      "💬",
    "portfolio": "🎨",
    "docs":      "📚",
}


def print_result(info):
    print()
    print(f"{BOLD}{CYAN}╔══════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║              🔍  Анализ проекта — Smart Icon Picker                 ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════════════════╝{RESET}")
    print()

    # Фреймворк
    fw = info["framework"] or "unknown"
    emoji, label = FW_LABELS.get(fw, ("📁", fw))
    print(f"  {BOLD}Фреймворк:{RESET}    {emoji} {BOLD}{YELLOW}{label}{RESET}")

    # PM
    if info.get("package_manager") and info["framework"] not in ("django", "flask", "fastapi", "rails", "html"):
        pm_colors = {"npm": WHITE, "pnpm": ORANGE, "yarn": CYAN, "bun": YELLOW}
        pm = info["package_manager"]
        print(f"  {BOLD}Пакет. менеджер:{RESET} {pm_colors.get(pm, WHITE)}{pm}{RESET}")

    # UI-библиотека
    if info.get("ui_library"):
        print(f"  {BOLD}UI-библиотека:{RESET} {GREEN}{info['ui_library']}{RESET}")

    # Стилизация
    if info.get("styling"):
        print(f"  {BOLD}Стилизация:{RESET}   {CYAN}{info['styling']}{RESET}")

    # Тип проекта
    if info.get("project_type"):
        pt = info["project_type"]
        print(f"  {BOLD}Тип проекта:{RESET}  {PTYPE_EMOJI.get(pt, '📁')} {MAGENTA}{pt}{RESET}")

    # Уже установленные иконки
    if info.get("existing_icons"):
        names = ", ".join(e["name"] for e in info["existing_icons"])
        print(f"  {BOLD}Уже есть:{RESET}    {DIM}{names}{RESET}")

    print()
    print(f"  {'─' * 66}")
    print()

    # Рекомендация
    priority = info.get("recommendation_priority", "FRAMEWORK")
    pr_color, pr_label = PRIORITY_LABELS.get(priority, (WHITE, priority))

    print(f"  {BOLD}Рекомендую:{RESET}")
    print()
    print(f"  {BOLD}{GREEN}▶  {info['recommendation']}{RESET}  {DIM}(выбрано по: {pr_color}{pr_label}{RESET}{DIM}){RESET}")
    print()

    if info.get("recommendation_reason"):
        print(f"  {DIM}💡 {info['recommendation_reason']}{RESET}")
        print()

    # Установка
    if info.get("install_command"):
        print(f"  {BOLD}Установка:{RESET}")
        print(f"  {GREEN}{info['install_command']}{RESET}")
        print()

    # Импорт
    if info.get("import_example"):
        print(f"  {BOLD}Импорт:{RESET}")
        for line in info["import_example"].split("\n"):
            print(f"  {WHITE}{line}{RESET}")
        print()

    # Использование
    if info.get("usage_example"):
        print(f"  {BOLD}Использование:{RESET}")
        for line in info["usage_example"].split("\n"):
            print(f"  {WHITE}{line}{RESET}")
        print()

    # CDN (для HTML/Python)
    if info.get("cdn_example"):
        print(f"  {BOLD}Добавь в HTML:{RESET}")
        for line in info["cdn_example"].split("\n"):
            print(f"  {WHITE}{line}{RESET}")
        print()

    # Уже установлены — не дублировать
    if info.get("existing_icons"):
        existing_names = [e["name"] for e in info["existing_icons"]]
        if info["recommendation"] in existing_names or any(info["recommendation"] in e["package"] for e in info["existing_icons"]):
            print(f"  {GREEN}✅ Эта библиотека уже установлена! Просто импортируй и используй.{RESET}")
            print()

    print(f"  {'─' * 66}")
    print()

    # Цепочка рассуждений (debug)
    if "--debug" in sys.argv:
        print(f"  {DIM}Цепочка анализа:{RESET}")
        for step in info.get("reasoning_chain", []):
            print(f"  {DIM}  → {step}{RESET}")
        print()

    if "--json" in sys.argv:
        print("JSON_DATA:" + json.dumps(info, ensure_ascii=False))


def main():
    path = "."
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            path = arg
            break

    info = analyze(path)
    print_result(info)


if __name__ == "__main__":
    main()
