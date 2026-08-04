#!/usr/bin/env python3
"""
SVG Icons Library Browser
Показывает каталог лучших SVG библиотек иконок
"""

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
WHITE = "\033[97m"
RED = "\033[91m"

LIBRARIES = [
    {
        "rank": 1,
        "name": "Lucide",
        "count": "1,500+",
        "style": "Тонкие, минималистичные",
        "best_for": "React, Next.js, Vite",
        "url": "https://lucide.dev",
        "npm": "lucide-react",
        "cdn": "https://unpkg.com/lucide@latest",
        "color": CYAN,
        "stars": "⭐⭐⭐⭐⭐",
        "tag": "🏆 ЛУЧШИЙ ВЫБОР",
    },
    {
        "rank": 2,
        "name": "Phosphor Icons",
        "count": "9,000+",
        "style": "6 вариантов толщины (thin → bold)",
        "best_for": "Дизайн-системы, любой стек",
        "url": "https://phosphoricons.com",
        "npm": "@phosphor-icons/react",
        "cdn": "https://unpkg.com/@phosphor-icons/web",
        "color": MAGENTA,
        "stars": "⭐⭐⭐⭐⭐",
        "tag": "🎨 МАКСИМУМ ИКОНОК",
    },
    {
        "rank": 3,
        "name": "Heroicons",
        "count": "292+",
        "style": "Outline + Solid, Tailwind-стиль",
        "best_for": "Tailwind CSS проекты",
        "url": "https://heroicons.com",
        "npm": "@heroicons/react",
        "cdn": None,
        "color": BLUE,
        "stars": "⭐⭐⭐⭐",
        "tag": "💎 ДЛЯ TAILWIND",
    },
    {
        "rank": 4,
        "name": "Tabler Icons",
        "count": "5,000+",
        "style": "Stroke-иконки, чёткие",
        "best_for": "Дашборды, админки",
        "url": "https://tabler.io/icons",
        "npm": "@tabler-icons-react",
        "cdn": "https://unpkg.com/@tabler/icons@latest",
        "color": GREEN,
        "stars": "⭐⭐⭐⭐⭐",
        "tag": "📊 ДЛЯ ДАШБОРДОВ",
    },
    {
        "rank": 5,
        "name": "Iconify",
        "count": "200,000+",
        "style": "Все стили — агрегатор библиотек",
        "best_for": "Когда нужны ВСЕ иконки сразу",
        "url": "https://icon-sets.iconify.design",
        "npm": "@iconify/react",
        "cdn": "https://code.iconify.design/iconify-icon/2.1.0/iconify-icon.min.js",
        "color": YELLOW,
        "stars": "⭐⭐⭐⭐⭐",
        "tag": "🌐 ВСЁ СРАЗУ",
    },
    {
        "rank": 6,
        "name": "Remix Icon",
        "count": "2,800+",
        "style": "Line + Fill, нейтральный дизайн",
        "best_for": "Любой проект, нейтральный стиль",
        "url": "https://remixicon.com",
        "npm": "remixicon",
        "cdn": "https://cdn.jsdelivr.net/npm/remixicon@4.0.0/fonts/remixicon.min.css",
        "color": RED,
        "stars": "⭐⭐⭐⭐",
        "tag": None,
    },
    {
        "rank": 7,
        "name": "Radix Icons",
        "count": "300+",
        "style": "Ultra-минималистичные 15px",
        "best_for": "Radix UI, Shadcn/UI проекты",
        "url": "https://www.radix-ui.com/icons",
        "npm": "@radix-ui/react-icons",
        "cdn": None,
        "color": WHITE,
        "stars": "⭐⭐⭐⭐",
        "tag": None,
    },
    {
        "rank": 8,
        "name": "Bootstrap Icons",
        "count": "2,000+",
        "style": "Stroke + Fill, Bootstrap-стиль",
        "best_for": "Bootstrap проекты, HTML",
        "url": "https://icons.getbootstrap.com",
        "npm": "bootstrap-icons",
        "cdn": "https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css",
        "color": MAGENTA,
        "stars": "⭐⭐⭐⭐",
        "tag": None,
    },
    {
        "rank": 9,
        "name": "Material Symbols",
        "count": "3,000+",
        "style": "Google Material Design",
        "best_for": "Google-стиль интерфейсы",
        "url": "https://fonts.google.com/icons",
        "npm": "@mui/icons-material",
        "cdn": "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined",
        "color": CYAN,
        "stars": "⭐⭐⭐⭐",
        "tag": None,
    },
    {
        "rank": 10,
        "name": "Hugeicons",
        "count": "4,000+",
        "style": "Детализированные, премиум",
        "best_for": "Премиум дизайн, SaaS продукты",
        "url": "https://hugeicons.com",
        "npm": "hugeicons-react",
        "cdn": None,
        "color": YELLOW,
        "stars": "⭐⭐⭐⭐",
        "tag": "✨ ПРЕМИУМ",
    },
]

SPECIAL = [
    {"name": "Simple Icons", "desc": "Логотипы 3000+ брендов", "url": "https://simpleicons.org", "npm": "simple-icons"},
    {"name": "Devicons", "desc": "Языки и технологии", "url": "https://devicon.dev", "npm": "devicon"},
    {"name": "Flag Icons", "desc": "Флаги всех стран", "url": "https://flagicons.lipis.dev", "npm": "flag-icons"},
    {"name": "Font Awesome", "desc": "Классика, 2000+ бесплатных", "url": "https://fontawesome.com", "npm": "@fortawesome/free-solid-svg-icons"},
]

def print_header():
    print()
    print(f"{BOLD}{CYAN}╔══════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║          🎨  SVG Icon Libraries — Лучшие библиотеки иконок          ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════════════════╝{RESET}")
    print()

def print_library(lib):
    color = lib["color"]
    tag = f"  {BOLD}{YELLOW}{lib['tag']}{RESET}" if lib["tag"] else ""
    print(f"  {BOLD}{color}[{lib['rank']:02d}] {lib['name']}{RESET} {lib['stars']}{tag}")
    print(f"       {WHITE}Иконок:{RESET} {BOLD}{lib['count']:<10}{RESET}  {WHITE}Стиль:{RESET} {lib['style']}")
    print(f"       {WHITE}Лучше всего для:{RESET} {DIM}{lib['best_for']}{RESET}")
    print(f"       {WHITE}Сайт:{RESET}  {CYAN}{lib['url']}{RESET}")
    print(f"       {WHITE}npm:{RESET}   {GREEN}npm install {lib['npm']}{RESET}")
    if lib["cdn"]:
        print(f"       {WHITE}CDN:{RESET}   {DIM}{lib['cdn'][:60]}{'...' if len(lib['cdn']) > 60 else ''}{RESET}")
    print()

def print_special():
    print(f"  {BOLD}{YELLOW}── Специализированные ──────────────────────────────────{RESET}")
    print()
    for lib in SPECIAL:
        print(f"  {BOLD}• {lib['name']}{RESET} — {lib['desc']}")
        print(f"    {CYAN}{lib['url']}{RESET}  |  {GREEN}npm install {lib['npm']}{RESET}")
    print()

def print_tip():
    print(f"  {BOLD}{CYAN}── Совет ───────────────────────────────────────────────{RESET}")
    print()
    print(f"  {BOLD}Используй Iconify{RESET} — одна установка даёт доступ ко ВСЕМ библиотекам:")
    print(f"  {GREEN}npm install @iconify/react{RESET}")
    print()
    print(f"  {DIM}Тогда используй любую иконку из любой библиотеки:{RESET}")
    print(f"  {WHITE}<Icon icon=\"lucide:home\" />        ← Lucide{RESET}")
    print(f"  {WHITE}<Icon icon=\"ph:rocket\" />          ← Phosphor{RESET}")
    print(f"  {WHITE}<Icon icon=\"tabler:dashboard\" />   ← Tabler{RESET}")
    print(f"  {WHITE}<Icon icon=\"heroicons:heart\" />    ← Heroicons{RESET}")
    print()
    print(f"  {BOLD}{MAGENTA}  Поиск иконок:{RESET} {CYAN}https://icon-sets.iconify.design{RESET}")
    print()

def print_footer():
    print(f"  {'─' * 66}")
    print()
    print(f"  {BOLD}Выбери библиотеку{RESET} (напиши номер или название)")
    print(f"  {DIM}или скажи «добавь иконки в мой проект» — AGY определит стек автоматически{RESET}")
    print()

def main():
    print_header()
    for lib in LIBRARIES:
        print_library(lib)
    print_special()
    print_tip()
    print_footer()

if __name__ == "__main__":
    main()
