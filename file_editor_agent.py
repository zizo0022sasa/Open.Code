#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
════════════════════════════════════════════════════════════════════════════════
🛡️ بيئة عمل أنتيجرافيتي المعزولة — محرك التعديل الجراحي المتقدم v4.0 (Enterprise)
════════════════════════════════════════════════════════════════════════════════
📍 مسار البيئة المعزولة: D:\SMS\.hRhR_gateway-service\_antigravity_workspace\
المميزات المطورة وفق توصيات الخبير المعماري المستقل (M1 Core):
  1. 🎯 نظام المطابقة الخماسي (5-Level Resilient Matcher):
     - المستوى 1: مطابقة دقيقة (Exact Match).
     - المستوى 2: تطبيع نهايات سطور ويندوز (CRLF / EOL Normalization).
     - المستوى 3: تطبيع المسافات والتبويبات (Whitespace Collapse).
     - المستوى 4: مطابقة ضبابية بنسبة توافق عالية (Fuzzy Match > 82%).
     - المستوى 5: فشل صريح وفوري (Fail-Fast) لمنع التعديل الخاطئ.
  2. 🛡️ صمام الأمان النحوي (AST Syntax Gate):
     - فحص كود بايثون تلقائياً بـ `ast.parse` قبل الحفظ لضمان عدم وجود أخطاء صياغة.
  3. 📂 دعم تعديل ملفات متعددة في نفس المهمة (Multi-File Atomic Transactions):
     - قراءة ترويسات الملفات (`FILE: ...` أو `# file: ...`).
     - تنفيذ معاملة ذرية: إما تطبيق كل التعديلات بنجاح أو التراجع الكامل (Rollback).
  4. ⏱️ شرط توقف حتمي (Deterministic Stop Condition - Max 3 Retries).
  5. 📊 عرض Diff ملون وواضح على سطر الأوامر.
════════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import re
import ast
import time
import difflib
import argparse

# ضبط ترميز UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# إعداد مسارات استيراد محرك Upstage محلياً أو من مجلد engine
current_dir = os.path.dirname(os.path.abspath(__file__))
engine_dir = os.path.join(current_dir, "engine")
if os.path.exists(engine_dir):
    sys.path.insert(0, engine_dir)

UPSTAGE_DIR = r"D:\SMS\.hRhR_gateway-service\.AAA_GGG_iii_VIBE_CODING_مجلد_المزودين\studio.upstage.ai"
if os.path.exists(UPSTAGE_DIR):
    sys.path.insert(0, UPSTAGE_DIR)

try:
    from ask_question import ask_upstage
except ImportError:
    raise RuntimeError("تعذر العثور على محرك Upstage في مسار المزودين!")


MODELS_LIST = [
    ("auto", "Auto Pilot (الموديل الافتراضي الذكي مع Very high thinking)"),
    ("gpt-5.4", "GPT-5.4 (الأقوى في البرمجة وهندسة النظم المعقدة)"),
    ("claude-fable-5.1-maximum", "Claude Fable 5.1 Maximum (دقيق جداً في التحليل والصياغة)"),
    ("solar-pro4", "Solar Pro 4 (موديل أبستيج فائق السرعة)"),
    ("gemini-2.5-flash", "Gemini 2.5 Flash (سريع وخفيف)")
]


# ════════════════════════════════════════════════════════════════════════════
# 🧩 دوال تطبيع وتدقيق النصوص ومطابقة كتل SEARCH/REPLACE (طبقة M1)
# ════════════════════════════════════════════════════════════════════════════

def norm_eol(text: str) -> str:
    """تطبيع نهايات الأسطر لنظام موحد (LF) لحل مشكلة Windows CRLF"""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def collapse_whitespace(text: str) -> str:
    """إزالة المسافات الزائدة في نهايات وبدايات السطور للمطابقة المرنة"""
    lines = [re.sub(r"\s+", " ", line).strip() for line in norm_eol(text).splitlines()]
    return "\n".join(lines)


def match_and_replace_block(original_text: str, search_block: str, replace_block: str) -> tuple[str, str]:
    """
    محرك المطابقة الخماسي الحتمي:
    يرجع: (النص الجديد, نوع المطابقة: exact | eol | whitespace | fuzzy | FAILED)
    """
    # 1) مطابقة دقيقة أولاً
    if search_block in original_text:
        return original_text.replace(search_block, replace_block, 1), "exact"

    # 2) مطابقة بعد تطبيع EOL (Windows CRLF vs Unix LF)
    norm_orig = norm_eol(original_text)
    norm_search = norm_eol(search_block)
    norm_replace = norm_eol(replace_block)
    if norm_search in norm_orig:
        return norm_orig.replace(norm_search, norm_replace, 1), "eol"

    # 3) مطابقة مع تطبيع المسافات البيضاء والتبويبات
    s_lines = [re.sub(r"\s+", " ", l).strip() for l in norm_search.splitlines()]
    orig_lines = norm_orig.splitlines()
    s_len = len(s_lines)

    if s_len > 0 and s_len <= len(orig_lines):
        for i in range(len(orig_lines) - s_len + 1):
            window = [re.sub(r"\s+", " ", orig_lines[i + k]).strip() for k in range(s_len)]
            if window == s_lines:
                # وجدنا تطابق المسافات
                prefix = orig_lines[:i]
                suffix = orig_lines[i + s_len:]
                rep_lines = norm_replace.splitlines()
                return "\n".join(prefix + rep_lines + suffix), "whitespace"

    # 4) مطابقة ضبابية (Fuzzy Window Match) بنسبة تطابق > 82%
    if s_len > 0 and s_len <= len(orig_lines):
        best_ratio = 0.0
        best_idx = -1
        search_str = "\n".join(s_lines)
        for i in range(len(orig_lines) - s_len + 1):
            candidate_str = "\n".join([re.sub(r"\s+", " ", orig_lines[i + k]).strip() for k in range(s_len)])
            ratio = difflib.SequenceMatcher(None, search_str, candidate_str).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_idx = i

        if best_ratio >= 0.82 and best_idx != -1:
            prefix = orig_lines[:best_idx]
            suffix = orig_lines[best_idx + s_len:]
            rep_lines = norm_replace.splitlines()
            return "\n".join(prefix + rep_lines + suffix), f"fuzzy ({int(best_ratio*100)}%)"

    # 5) فشل صريح — يمنع التخمين الخاطئ لحماية الكود
    return original_text, "FAILED"


def validate_python_syntax(code_str: str) -> tuple[bool, str]:
    """صمام الأمان: التحقق من خلو كود بايثون من أخطاء الـ Syntax والـ Indentation"""
    try:
        ast.parse(code_str)
        return True, "Valid"
    except SyntaxError as e:
        return False, f"SyntaxError at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


def parse_multi_file_patches(ai_text: str) -> list[dict]:
    """
    استخراج كتل التعديل مع دعم مسارات الملفات المتعددة:
    # file: path/to/file.py
    <<<<<<< SEARCH
    ...
    =======
    ...
    >>>>>>>
    """
    patches = []
    # نمط يبحث عن اسم الملف الاختياري يليه كتلة SEARCH/REPLACE
    pattern = r"(?:(?:#|//|--)?\s*(?:file|path):\s*([^\r\n]+)\r?\n)?<<<<<<<\s*SEARCH\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>>"
    matches = re.findall(pattern, ai_text, re.DOTALL | re.IGNORECASE)

    for m in matches:
        target_file = m[0].strip() if m[0] else ""
        search_b = m[1]
        replace_b = m[2]
        patches.append({
            "file": target_file,
            "search": search_b,
            "replace": replace_b
        })
    return patches


def print_colored_diff(old_text: str, new_text: str, filename: str = "file"):
    """عرض الـ Diff اللحظي بألوان واضحة على سطر الأوامر"""
    old_lines = norm_eol(old_text).splitlines(keepends=True)
    new_lines = norm_eol(new_text).splitlines(keepends=True)
    diff = list(difflib.unified_diff(old_lines, new_lines, fromfile=f"a/{filename}", tofile=f"b/{filename}", n=2))

    if not diff:
        print("   ℹ️ لا توجد فروقات نصية.")
        return

    print("┌" + "─" * 65 + "┐")
    for line in diff[:35]:  # عرض أول 35 سطر من الديف
        l_str = line.rstrip()
        if l_str.startswith("---") or l_str.startswith("+++"):
            print(f"│ \033[1m{l_str}\033[0m")
        elif l_str.startswith("@@"):
            print(f"│ \033[36m{l_str}\033[0m")
        elif l_str.startswith("-"):
            print(f"│ \033[31m{l_str}\033[0m")
        elif l_str.startswith("+"):
            print(f"│ \033[32m{l_str}\033[0m")
        else:
            print(f"│ {l_str}")
    if len(diff) > 35:
        print(f"│ ... [تم اختصار باقي الفروقات ({len(diff)-35} سطور إضافية)]")
    print("└" + "─" * 65 + "┘")


# ════════════════════════════════════════════════════════════════════════════
# 🚀 محرك التعديل الرئيسي والعمليات الذرية (Atomic Execution)
# ════════════════════════════════════════════════════════════════════════════

def execute_surgical_job(target_files: list[str], prompt: str, model: str = "auto", thinking: str = "xhigh", auto_save: bool = False, max_retries: int = 3):
    """
    تنفيذ مهمة التعديل الجراحي مع دعم تعدد الملفات والمعاملات الذرية
    """
    print(f"\n" + "═" * 65)
    print("🚀 [محرك التعديل الجراحي المتقدم v4.0]")
    print(f"🤖 الموديل: [{model}] | التفكير: [{thinking}] | الأذونات: [Skip permissions - bypass]")
    print(f"📄 الملفات المستهدفة: {len(target_files)} ملف")
    print("═" * 65)

    # 1. قراءة الملفات في الذاكرة (Memory Buffer)
    buffers = {}
    for fpath in target_files:
        abs_p = os.path.abspath(fpath)
        if os.path.exists(abs_p):
            with open(abs_p, "r", encoding="utf-8", errors="ignore") as f:
                buffers[abs_p] = f.read()
            print(f"   📖 تم تحميل: {os.path.basename(abs_p)} ({len(buffers[abs_p].splitlines())} سطر)")
        else:
            buffers[abs_p] = ""
            print(f"   ✨ ملف جديد سيتم إنشاؤه: {os.path.basename(abs_p)}")

    # 2. بناء سياق البرومبت
    context_blocks = []
    for abs_p, content in buffers.items():
        rel_name = os.path.basename(abs_p)
        context_blocks.append(f"FILE: {rel_name}\n```\n{content}\n```")

    full_context_str = "\n\n".join(context_blocks)
    surgical_prompt = (
        f"المحتوى الحالي لملفات المشروع في هذه المهمة:\n\n{full_context_str}\n\n"
        f"المطلوب تنفيذه وتعديله بدقة:\n{prompt}\n\n"
        f"⚠️ تنبيه معماري إلزامي:\n"
        f"- لا تعد كتابة الملفات بالكامل نهائياً!\n"
        f"- حدد فقط السطور أو الأجزاء التي تحتاج إلى تعديل أو تصحيح أو إضافة أو حذف.\n"
        f"- ضع ترويسة اسم الملف قبل كل كتلة: `FILE: filename` ثم صيغة SEARCH / REPLACE:\n\n"
        f"FILE: filename.ext\n"
        f"<<<<<<< SEARCH\n"
        f"[السطور القديمة الموجودة في الملف بالضبط بدون تغيير]\n"
        f"=======\n"
        f"[السطور الجديدة المعدلة بدلاً منها]\n"
        f">>>>>>>\n"
    )

    for attempt in range(1, max_retries + 1):
        print(f"\n⏳ جاري استلام التعديلات الجراحية من السحابة (محاولة {attempt}/{max_retries})...")
        ai_raw = ask_upstage(prompt=surgical_prompt, model=model, thinking=thinking, permission="bypass")
        patches = parse_multi_file_patches(ai_raw)

        if not patches:
            # لو الموديل رجع كتل بدون ترويسة ملف لملف واحد
            single_pattern = r"<<<<<<<\s*SEARCH\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>>"
            single_matches = re.findall(single_pattern, ai_raw, re.DOTALL)
            if single_matches and len(target_files) == 1:
                patches = [{"file": os.path.basename(target_files[0]), "search": sm[0], "replace": sm[1]} for sm in single_matches]

        if not patches:
            print("\n⚠️ لم يتم العثور على كتل SEARCH/REPLACE جراحية.")
            if len(target_files) == 1 and not os.path.exists(target_files[0]):
                # ملف جديد بالكامل
                cleaned = ai_raw.strip()
                if cleaned.startswith("```") and cleaned.endswith("```"):
                    lines = cleaned.splitlines()
                    if len(lines) >= 2:
                        cleaned = "\n".join(lines[1:-1]).strip()
                save_single_file(target_files[0], cleaned)
                return
            if attempt < max_retries:
                surgical_prompt += "\n\nتنبيه: التعديل يجب أن يكون حصراً بصيغة <<<<<<< SEARCH ... ======= ... >>>>>>>"
                continue
            else:
                print("❌ فشل الحصول على كتل جراحية صالحة بعد 3 محاولات.")
                return

        print(f"\n🎯 تم اكتشاف {len(patches)} كتلة تعديل جراحية!")

        # 3. اختبار التطبيق في الذاكرة (Atomic Dry-Run)
        new_buffers = dict(buffers)
        all_passed = True
        match_details = []

        for p_idx, p in enumerate(patches, 1):
            p_file = p["file"]
            # مطابقة اسم الملف
            target_p = None
            if p_file:
                for path_key in new_buffers:
                    if os.path.basename(path_key).lower() == p_file.lower():
                        target_p = path_key
                        break
            if not target_p and len(target_files) == 1:
                target_p = list(new_buffers.keys())[0]

            if not target_p:
                print(f"   ⚠️ تعذر تحديد مسار الملف للكتلة {p_idx} (الملف المذكور: {p_file})")
                all_passed = False
                break

            orig_c = new_buffers[target_p]
            mod_c, match_type = match_and_replace_block(orig_c, p["search"], p["replace"])

            if match_type == "FAILED":
                print(f"   ❌ فشلت مطابقة الكتلة رقم {p_idx} في {os.path.basename(target_p)}!")
                all_passed = False
                break
            else:
                new_buffers[target_p] = mod_c
                match_details.append((target_p, p_idx, match_type))

        # 4. إذا فشلت مطابقة أي كتلة -> تراجع كامل (Rollback) والمحاولة مرة أخرى
        if not all_passed:
            print(f"   🔄 تراجع كلي فوري (Atomic Rollback) لحماية الملفات!")
            if attempt < max_retries:
                surgical_prompt += "\n\nتنبيه: بعض كتل SEARCH لم تطابق النص في الملف، تأكد من نقل الأسطر بدقة متناهية."
                continue
            else:
                print("❌ تعذر تطبيق التعديلات بنجاح بعد 3 محاولات.")
                return

        # 5. صمام الأمان النحوي (AST Syntax Gate لملفات بايثون)
        syntax_errors = []
        for fpath, content in new_buffers.items():
            if fpath.endswith(".py"):
                is_valid, msg = validate_python_syntax(content)
                if not is_valid:
                    syntax_errors.append((os.path.basename(fpath), msg))

        if syntax_errors:
            print("\n🚨 تم اكتشاف خطأ صياغة (Syntax Error) قبل الحفظ!")
            for fname, err in syntax_errors:
                print(f"   ❌ {fname}: {err}")
            if attempt < max_retries:
                surgical_prompt += f"\n\nالكود المعدل أحدث خطأ بايثون: {syntax_errors[0][1]}. يرجى إصلاحه."
                continue
            else:
                print("❌ إلغاء العملية لمنع كتابة كود مكسور على القرص.")
                return

        # 6. عرض تقرير النجاح والـ Diff
        print("\n📊 تقرير التطبيق الجراحي:")
        for t_p, p_i, m_t in match_details:
            print(f"   ✅ كتلة {p_i} في [{os.path.basename(t_p)}]: مطابقة ناجحة ({m_t})")

        print("\n🔍 معاينة الفروقات (Diff Preview):")
        for fpath in target_files:
            abs_p = os.path.abspath(fpath)
            if abs_p in new_buffers:
                print_colored_diff(buffers[abs_p], new_buffers[abs_p], os.path.basename(abs_p))

        # 7. الحفظ على القرص الصلب (Commit)
        if auto_save:
            commit_buffers(new_buffers)
            return

        print("\n🤔 ماذا تريد أن تفعل؟")
        print("  [1] ✅ اعتماد وحفظ التعديلات فوراً (Commit)")
        print("  [2] 💾 حفظ كنسخ احتياطية (.updated)")
        print("  [3] ❌ إلغاء وتراجع كامل (Rollback)")
        choice = input("اختر خياراً [1/2/3] (افتراضي 1): ").strip()

        if choice in ["1", ""]:
            commit_buffers(new_buffers)
        elif choice == "2":
            for fpath, c in new_buffers.items():
                save_single_file(fpath + ".updated", c)
        else:
            print("🚫 تم التراجع الكامل ولم يتم تعديل أي ملف على القرص.")
        return


def commit_buffers(buffers: dict):
    """كتابة المعاملة الذرية على الهارد ديسك"""
    for fpath, content in buffers.items():
        save_single_file(fpath, content)
    print(f"\n🎉 تم اعتماد وحفظ جميع التعديلات بنجاح!")
    print("⚡ محررك قام بتحديث التبويبات المفتوحة تلقائياً!")


def save_single_file(file_path: str, content: str):
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"👉 تم حفظ: {os.path.abspath(file_path)}")


def run_watch_mode(file_path: str, model: str = "auto", thinking: str = "xhigh"):
    """وضع المراقبة اللحظية"""
    if not os.path.exists(file_path):
        print(f"❌ الملف غير موجود للمراقبة: {file_path}")
        return

    print("\n" + "═" * 65)
    print("👁️ [وضع المراقبة اللحظية الجراحي v4.0 - Auto Watcher]")
    print(f"📄 الملف المراقب: {file_path}")
    print(f"🤖 الموديل: {model} | التفكير: {thinking} | الأذونات: Skip permissions")
    print("💡 بمجرد ما تعدل وتعمل Ctrl+S، الذكاء الاصطناعي هيصلحه جراحياً ويفحص الـ Syntax فوراً!")
    print("💡 للخروج اضغط Ctrl+C في أي وقت.")
    print("═" * 65 + "\n")

    last_mtime = os.path.getmtime(file_path)
    while True:
        try:
            time.sleep(1)
            current_mtime = os.path.getmtime(file_path)
            if current_mtime != last_mtime:
                last_mtime = current_mtime
                time.sleep(0.5)

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                if not content.strip():
                    continue

                print(f"\n🔔 تم اكتشاف حفظ للملف! جاري المعالجة والفحص النحوي...")
                prompt = "صحح الأخطاء وعلامات الاستفهام والنواقص حصراً بصيغة SEARCH / REPLACE."
                execute_surgical_job([file_path], prompt, model=model, thinking=thinking, auto_save=True)
                last_mtime = os.path.getmtime(file_path)
        except (KeyboardInterrupt, EOFError):
            print("\nتم إيقاف المراقبة.")
            break


def interactive_menu():
    """الواجهة التفاعلية الرئيسية"""
    print("\n" + "═" * 65)
    print("🛡️ بيئة عمل أنتيجرافيتي المعزولة (Surgical Diff Engine v4.0)")
    print("═" * 65)
    print("🛡️ الأذونات: Skip permissions | 🧠 الموديل: Auto (Very high)")
    
    file_input = input("\n📂 أدخل مسار الملف أو الملفات (افصل بينها بمسافة أو اسحبها هنا):\n❯ ").strip().strip('"').strip("'")
    if not file_input:
        print("❌ لم يتم إدخال أي مسار.")
        return

    # استخراج المسارات (دعم السحب والإفلات لعدة ملفات)
    raw_files = [p.strip().strip('"').strip("'") for p in file_input.split() if p.strip()]
    target_files = [os.path.abspath(p) for p in raw_files]

    print("\n🎯 اختر نوع العملية:")
    print("  [1] ⚡ تعديل جراحي ذري (Surgical Diff - تصحيح، إضافة، حل)")
    print("  [2] 👁️ تشغيل وضع المراقبة التلقائية (Auto Watcher on Ctrl+S)")
    op_choice = input("اختر [1 أو 2] (افتراضي 1): ").strip()

    if op_choice == "2":
        if len(target_files) > 0:
            run_watch_mode(target_files[0], model="auto", thinking="xhigh")
        return

    prompt = input("\n📝 ما المطلوب تنفيذه في الملفات بالضبط؟\n❯ ").strip()
    if not prompt:
        print("❌ لم يتم كتابة أي تعليمات.")
        return

    execute_surgical_job(target_files, prompt, model="auto", thinking="xhigh", auto_save=False)


def main():
    parser = argparse.ArgumentParser(description="Universal AI File Editor Agent v4.0 (Enterprise)")
    parser.add_argument("files", nargs="*", default=None, help="مسار الملف أو الملفات المستهدفة")
    parser.add_argument("--prompt", "-p", type=str, default=None, help="التعليمات المطلوب تنفيذها")
    parser.add_argument("--model", "-m", type=str, default="auto", help="الموديل المراد استخدامه")
    parser.add_argument("--thinking", "-t", type=str, default="xhigh", help="جهد التفكير (افتراضي xhigh)")
    parser.add_argument("--auto-save", action="store_true", help="حفظ الملف تلقائياً")
    parser.add_argument("--watch", "-w", action="store_true", help="تشغيل وضع المراقبة التلقائية")

    args = parser.parse_args()

    if args.files and args.watch:
        run_watch_mode(os.path.abspath(args.files[0]), model=args.model, thinking=args.thinking)
    elif args.files and args.prompt:
        target_files = [os.path.abspath(f) for f in args.files]
        execute_surgical_job(target_files, args.prompt, model=args.model, thinking=args.thinking, auto_save=args.auto_save)
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
