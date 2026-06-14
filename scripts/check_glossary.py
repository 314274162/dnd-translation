#!/usr/bin/env python3
"""
DND 翻译项目 - 术语一致性校验工具

功能：
1. 从 GLOSSARY.md 提取术语表
2. 扫描翻译文件，检查术语是否与术语表一致
3. 报告不一致或缺失的术语

使用方法：
    python3 check_glossary.py <翻译文件路径>
"""

import re
import sys
import os
from pathlib import Path


def load_glossary(glossary_path: str) -> dict:
    """从术语字典中提取英中术语对照"""
    glossary = {}
    
    if not os.path.exists(glossary_path):
        print(f"[警告] 术语字典不存在: {glossary_path}")
        return glossary
    
    with open(glossary_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 匹配表格行：| 英文 | 中文 | ... |
    # 跳过表头和分隔行
    lines = content.split("\n")
    in_table = False
    
    for line in lines:
        line = line.strip()
        if line.startswith("|---") or line.startswith("| # |"):
            continue
        if line.startswith("|") and not line.startswith("| #"):
            parts = [p.strip() for p in line.split("|")]
            # 有效数据行通常至少有3列（含首尾空）
            valid_parts = [p for p in parts if p]
            if len(valid_parts) >= 2:
                en = valid_parts[0].strip()
                cn = valid_parts[1].strip()
                # 跳过非术语行（纯中文、标点、空等）
                if en and cn and re.search(r'[a-zA-Z]', en):
                    glossary[en.lower()] = cn
    
    return glossary


def scan_translation(file_path: str, glossary: dict) -> list:
    """扫描翻译文件，检查术语使用情况"""
    issues = []
    
    if not os.path.exists(file_path):
        return [f"[错误] 文件不存在: {file_path}"]
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 提取所有英文单词/短语
    words = set(re.findall(r'\b[A-Za-z][A-Za-z\s\-\']{2,30}\b', content))
    
    # 检查是否有术语表中未收录的英文术语
    for word in words:
        word_lower = word.lower().strip()
        if word_lower in glossary:
            # 术语已收录，检查翻译是否出现
            expected_cn = glossary[word_lower]
            # 简化检查：看中文翻译是否在文件中出现
            if expected_cn not in content:
                issues.append(f"[术语缺失翻译] '{word}' -> 应译为'{expected_cn}'，但未在文件中找到该译法")
    
    return issues


def main():
    project_root = Path(__file__).parent.parent
    glossary_path = project_root / "glossary" / "GLOSSARY.md"
    
    glossary = load_glossary(str(glossary_path))
    print(f"已加载 {len(glossary)} 条术语")
    
    if len(sys.argv) < 2:
        print("用法: python3 check_glossary.py <翻译文件路径>")
        print("示例: python3 check_glossary.py ../output/core-rules/chapter1.md")
        sys.exit(1)
    
    target_file = sys.argv[1]
    issues = scan_translation(target_file, glossary)
    
    if issues:
        print(f"\n发现 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n未发现问题。")
    
    return len(issues)


if __name__ == "__main__":
    sys.exit(main())
