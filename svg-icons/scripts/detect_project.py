#!/usr/bin/env python3
"""
Project Type Detector for SVG Icons Skill
Определяет тип проекта и рекомендует подходящую библиотеку иконок
"""

import json
import os
import sys

def detect_project(path="."):
    path = os.path.abspath(path)
    result = {
        "path": path,
        "type": "unknown",
        "framework": None,
        "package_manager": "npm",
        "recommended_library": None,
        "install_command": None,
        "import_example": None,
        "usage_example": None,
    }

    # Проверяем package.json
    pkg_path = os.path.join(path, "package.json")
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path) as f:
                pkg = json.load(f)
            deps = {
                **pkg.get("dependencies", {}),
                **pkg.get("devDependencies", {}),
            }

            # Определяем пакетный менеджер
            if os.path.exists(os.path.join(path, "pnpm-lock.yaml")):
                result["package_manager"] = "pnpm"
            elif os.path.exists(os.path.join(path, "yarn.lock")):
                result["package_manager"] = "yarn"
            else:
                result["package_manager"] = "npm"

            pm = result["package_manager"]

            # Next.js
            if "next" in deps:
                result["type"] = "javascript"
                result["framework"] = "Next.js"
                result["recommended_library"] = "lucide-react"
                result["install_command"] = f"{pm} install lucide-react"
                result["import_example"] = "import { Home, Search, Bell, User, Settings, Heart, Star, ArrowRight } from 'lucide-react'"
                result["usage_example"] = "<Home size={24} className=\"text-blue-500\" />"

            # React (без Next)
            elif "react" in deps:
                result["type"] = "javascript"
                result["framework"] = "React"
                result["recommended_library"] = "lucide-react"
                result["install_command"] = f"{pm} install lucide-react"
                result["import_example"] = "import { Home, Search, Bell, User, Settings } from 'lucide-react'"
                result["usage_example"] = "<Home size={24} color=\"currentColor\" />"

            # Vue / Nuxt
            elif "vue" in deps or "nuxt" in deps:
                fw = "Nuxt" if "nuxt" in deps else "Vue"
                result["type"] = "javascript"
                result["framework"] = fw
                result["recommended_library"] = "lucide-vue-next"
                result["install_command"] = f"{pm} install lucide-vue-next"
                result["import_example"] = "import { Home, Search, Bell } from 'lucide-vue-next'"
                result["usage_example"] = "<Home :size=\"24\" />"

            # Svelte / SvelteKit
            elif "svelte" in deps:
                fw = "SvelteKit" if "@sveltejs/kit" in deps else "Svelte"
                result["type"] = "javascript"
                result["framework"] = fw
                result["recommended_library"] = "lucide-svelte"
                result["install_command"] = f"{pm} install lucide-svelte"
                result["import_example"] = "import { Home, Search, Bell } from 'lucide-svelte'"
                result["usage_example"] = "<Home size={24} />"

            # Astro
            elif "astro" in deps:
                result["type"] = "javascript"
                result["framework"] = "Astro"
                result["recommended_library"] = "@iconify/react"
                result["install_command"] = f"{pm} install @iconify/react"
                result["import_example"] = "import { Icon } from '@iconify/react'"
                result["usage_example"] = "<Icon icon=\"lucide:home\" width=\"24\" />"

            # Обычный Node/Vite без фреймворка
            else:
                result["type"] = "javascript"
                result["framework"] = "Vanilla JS / Vite"
                result["recommended_library"] = "lucide"
                result["install_command"] = f"{pm} install lucide"
                result["import_example"] = "import { createIcons, Home, Search } from 'lucide'"
                result["usage_example"] = "createIcons()"

        except Exception:
            pass

    # Python / Django / Flask
    if result["type"] == "unknown":
        has_templates = os.path.exists(os.path.join(path, "templates"))
        has_manage = os.path.exists(os.path.join(path, "manage.py"))
        has_app = os.path.exists(os.path.join(path, "app.py")) or os.path.exists(os.path.join(path, "main.py"))
        py_files = [f for f in os.listdir(path) if f.endswith(".py")]

        if has_manage or (has_templates and py_files):
            result["type"] = "python"
            result["framework"] = "Django" if has_manage else "Flask"
            result["recommended_library"] = "Bootstrap Icons (CDN)"
            result["install_command"] = None
            result["import_example"] = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css">'
            result["usage_example"] = '<i class="bi bi-house"></i>'

        elif has_app and py_files:
            result["type"] = "python"
            result["framework"] = "Flask/FastAPI"
            result["recommended_library"] = "Iconify (CDN)"
            result["install_command"] = None
            result["import_example"] = '<script src="https://code.iconify.design/iconify-icon/2.1.0/iconify-icon.min.js"></script>'
            result["usage_example"] = '<iconify-icon icon="lucide:home"></iconify-icon>'

    # Vanilla HTML
    if result["type"] == "unknown":
        html_files = [f for f in os.listdir(path) if f.endswith(".html")]
        if html_files:
            result["type"] = "html"
            result["framework"] = "Vanilla HTML"
            result["recommended_library"] = "Lucide (CDN)"
            result["install_command"] = None
            result["import_example"] = '<script src="https://unpkg.com/lucide@latest"></script>'
            result["usage_example"] = '<i data-lucide="home"></i>\n<script>lucide.createIcons();</script>'

    return result


RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
DIM = "\033[2m"
WHITE = "\033[97m"
RED = "\033[91m"

FRAMEWORK_EMOJI = {
    "Next.js": "⚡",
    "React": "⚛️",
    "Vue": "💚",
    "Nuxt": "💚",
    "Svelte": "🔥",
    "SvelteKit": "🔥",
    "Astro": "🚀",
    "Vanilla JS / Vite": "⚡",
    "Django": "🐍",
    "Flask": "🐍",
    "Flask/FastAPI": "🐍",
    "Vanilla HTML": "🌐",
}

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    info = detect_project(path)

    print()
    print(f"  {BOLD}{CYAN}── Определение проекта ─────────────────────────────────{RESET}")
    print()

    fw = info["framework"] or "Неизвестно"
    emoji = FRAMEWORK_EMOJI.get(fw, "📁")

    if info["framework"]:
        print(f"  {BOLD}Проект:{RESET} {emoji} {BOLD}{YELLOW}{fw}{RESET}")
        print(f"  {BOLD}Путь:{RESET}   {DIM}{info['path']}{RESET}")
        if info["package_manager"] and info["type"] == "javascript":
            print(f"  {BOLD}Пакетный менеджер:{RESET} {GREEN}{info['package_manager']}{RESET}")
        print()
        print(f"  {BOLD}Рекомендую:{RESET} {BOLD}{CYAN}{info['recommended_library']}{RESET}")
        print()

        if info["install_command"]:
            print(f"  {BOLD}Установка:{RESET}")
            print(f"  {GREEN}{info['install_command']}{RESET}")
            print()

        if info["import_example"]:
            print(f"  {BOLD}Импорт:{RESET}")
            print(f"  {WHITE}{info['import_example']}{RESET}")
            print()

        if info["usage_example"]:
            print(f"  {BOLD}Использование:{RESET}")
            for line in info["usage_example"].split("\n"):
                print(f"  {WHITE}{line}{RESET}")
            print()
    else:
        print(f"  {YELLOW}⚠ Тип проекта не определён{RESET}")
        print(f"  Скажи AGY какой у тебя стек — он подберёт нужную библиотеку")
        print()

    print(f"  {'─' * 56}")
    print()

    # JSON для AGY
    if "--json" in sys.argv:
        print("JSON_DATA:" + json.dumps(info))


if __name__ == "__main__":
    main()
