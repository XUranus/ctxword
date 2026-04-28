"""Local dictionary fallback - basic word explanations without LLM."""

import json

# Minimal dictionary for common programming terms
_PROGRAMMING_TERMS: dict[str, dict] = {
    "pending": {
        "meaning_zh": "尚未完成；等待处理",
        "meaning_en": "not yet completed, decided, or resolved",
        "pos": ["adjective"],
        "domain": ["programming"],
        "note": "In async programming, a pending Promise has not been fulfilled or rejected yet.",
    },
    "async": {
        "meaning_zh": "异步",
        "meaning_en": "not happening at the same time; non-blocking execution",
        "pos": ["adjective"],
        "domain": ["programming"],
    },
    "await": {
        "meaning_zh": "等待",
        "meaning_en": "wait for a Promise or async operation to complete",
        "pos": ["verb"],
        "domain": ["programming", "async"],
    },
    "promise": {
        "meaning_zh": "Promise 对象；承诺",
        "meaning_en": "an object representing eventual completion or failure of an async operation",
        "pos": ["noun"],
        "domain": ["programming", "async", "javascript"],
    },
    "callback": {
        "meaning_zh": "回调函数",
        "meaning_en": "a function passed as an argument to be executed later",
        "pos": ["noun"],
        "domain": ["programming"],
    },
    "resolve": {
        "meaning_zh": "解析；解决；完成（Promise）",
        "meaning_en": "to determine, settle, or complete successfully",
        "pos": ["verb"],
        "domain": ["programming", "dns", "dependency-management"],
    },
    "reject": {
        "meaning_zh": "拒绝；驳回",
        "meaning_en": "to refuse, decline, or fail a Promise",
        "pos": ["verb"],
        "domain": ["programming", "javascript"],
    },
    "panic": {
        "meaning_zh": "内核恐慌；程序崩溃",
        "meaning_en": "an unrecoverable fatal error that stops execution",
        "pos": ["noun", "verb"],
        "domain": ["programming", "linux", "golang"],
    },
    "mount": {
        "meaning_zh": "挂载；安装",
        "meaning_en": "to attach a filesystem or make a resource accessible",
        "pos": ["verb"],
        "domain": ["linux", "filesystem"],
    },
    "yield": {
        "meaning_zh": "产出；让出（控制权）",
        "meaning_en": "to produce a value or relinquish execution control",
        "pos": ["verb", "noun"],
        "domain": ["programming", "python", "concurrency"],
    },
    "buffer": {
        "meaning_zh": "缓冲区",
        "meaning_en": "temporary storage area for data being transferred",
        "pos": ["noun", "verb"],
        "domain": ["programming", "systems"],
    },
    "cache": {
        "meaning_zh": "缓存",
        "meaning_en": "a hardware or software component that stores data for faster future access",
        "pos": ["noun", "verb"],
        "domain": ["programming", "systems"],
    },
    "flush": {
        "meaning_zh": "刷新；清空（缓冲区）",
        "meaning_en": "to forcefully write buffered data to its destination",
        "pos": ["verb"],
        "domain": ["programming", "io"],
    },
    "race condition": {
        "meaning_zh": "竞态条件",
        "meaning_en": "a situation where behavior depends on timing or ordering of concurrent operations",
        "pos": ["noun"],
        "domain": ["programming", "concurrency"],
    },
    "deadlock": {
        "meaning_zh": "死锁",
        "meaning_en": "a situation where two or more processes are waiting for each other indefinitely",
        "pos": ["noun"],
        "domain": ["programming", "concurrency"],
    },
    "middleware": {
        "meaning_zh": "中间件",
        "meaning_en": "software that acts as a bridge between an operating system or database and applications",
        "pos": ["noun"],
        "domain": ["programming", "web"],
    },
    "refactor": {
        "meaning_zh": "重构",
        "meaning_en": "to restructure existing code without changing its external behavior",
        "pos": ["verb"],
        "domain": ["programming"],
    },
    "idempotent": {
        "meaning_zh": "幂等的",
        "meaning_en": "an operation that produces the same result regardless of how many times it is performed",
        "pos": ["adjective"],
        "domain": ["programming", "api", "math"],
    },
    "immutable": {
        "meaning_zh": "不可变的",
        "meaning_en": "unable to be changed after creation",
        "pos": ["adjective"],
        "domain": ["programming", "functional-programming"],
    },
    "singleton": {
        "meaning_zh": "单例",
        "meaning_en": "a design pattern restricting a class to a single instance",
        "pos": ["noun"],
        "domain": ["programming", "design-patterns"],
    },
    "working tree": {
        "meaning_zh": "工作树",
        "meaning_en": "the directory of files you are currently working on in a git repository",
        "pos": ["noun"],
        "domain": ["git", "version-control"],
    },
    "side effect": {
        "meaning_zh": "副作用",
        "meaning_en": "a change in state or interaction with the outside world beyond returning a value",
        "pos": ["noun"],
        "domain": ["programming", "functional-programming"],
    },
    "breaking change": {
        "meaning_zh": "破坏性变更",
        "meaning_en": "a change that makes existing code or APIs incompatible",
        "pos": ["noun"],
        "domain": ["programming", "api-design"],
    },
}


def lookup(query: str) -> dict | None:
    """Look up a word or phrase in the local dictionary.

    Returns a dict with explanation data, or None if not found.
    """
    key = query.lower().strip()
    if key in _PROGRAMMING_TERMS:
        entry = _PROGRAMMING_TERMS[key]
        return {
            "query": query,
            "lemma": key,
            "part_of_speech": entry.get("pos", []),
            "meaning_zh": entry.get("meaning_zh", ""),
            "meaning_en": entry.get("meaning_en", ""),
            "context_explanation": entry.get("note"),
            "technical_domain": entry.get("domain", []),
            "collocations": entry.get("collocations", []),
            "examples": entry.get("examples", []),
            "common_mistakes": entry.get("common_mistakes", []),
            "cards": entry.get("cards", []),
            "_source": "local_dict",
        }
    return None
