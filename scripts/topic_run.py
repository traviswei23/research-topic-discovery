"""Validate a topic-discovery register and render the selected questions for handoff."""
import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def words(row, fields):
    for key in fields.split():
        need(isinstance(row.get(key), str) and row[key].strip(), f"缺少字段 {key}（{row.get('id', '记录')}）")


def array(row, name):
    value = row.get(name)
    need(isinstance(value, list), f"{name} 应为数组")
    return value


def keyed(row, field):
    out = {}
    for item in array(row, field):
        need(isinstance(item, dict), f"{field} 中有非对象条目")
        words(item, "id")
        need(item["id"] not in out, f"{field} 编号重复 {item['id']}")
        out[item["id"]] = item
    return out


def local(root, name):
    need(isinstance(name, str) and name.strip() and not Path(name).is_absolute(), "附件须使用项目相对路径")
    path = (root / name).resolve()
    need(root in path.parents and path.is_file() and path.stat().st_size, f"附件缺失、为空或越界 {name}")
    return path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_export(query, path):
    if path.suffix.lower() != ".json":
        return
    receipt = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(receipt, dict) or receipt.get("action") != "search" or "providers" not in receipt:
        return
    source = query["source"].strip().casefold()
    providers = receipt["providers"]
    need(query["operation"] == "search" and source in providers, "搜索回包与渠道或操作不符")
    result = providers[source]
    need(query["query"] == receipt["parameters"]["public_query"], "查询与保存的实际回包不符")
    status = {"ok": "ok", "zero_hits": "ok", "partial": "partial", "failed": "failed"}
    need(query["status"] == status.get(result["status"]), "查询状态与回包不符")
    if query["status"] == "ok":
        need(query["screened"] <= len(result["candidates"]), "筛读数超过实际导出条数")


def check(data, root):
    need(isinstance(data, dict) and data.get("version") == 1, "无法识别的档案版本")
    words(data, "direction constraints scope stop next_step")
    target = data.get("target")
    need(type(target) is int and target >= 1, "target 应为用户需要的正整数")
    papers, queries, cards = [keyed(data, key) for key in ("papers", "queries", "ideas")]
    need(bool(cards), "候选集为空")
    scope = data["scope"]
    need(scope in ("online", "provided_only"), "scope 必须为 online 或 provided_only")
    searched = set()
    for q in queries.values():
        words(q, "source query date operation status trace")
        date.fromisoformat(q["date"])
        trace = local(root, q["trace"])
        need(q["operation"] in ("search", "lookup", "citation"), "查询类型有误")
        need(q["status"] in ("ok", "partial", "failed"), "查询状态有误")
        if q["status"] == "ok":
            n = q.get("screened")
            need(type(n) is int and n >= 0, "须记录实际检查条数")
            if n > 0 and q["operation"] == "search":
                searched.add(q["source"].strip().casefold())
        else:
            words(q, "reason")
        check_export(q, trace)
    if scope == "online" and data.get("decision") != "partial":
        need(len(searched) >= 2, "正式联网选题需要两个实际筛读过的文献来源")
    elif scope == "provided_only":
        words(data, "scope_reason")
    for p in papers.values():
        words(p, "citation source locator observation level")
        need(p["level"] in ("original", "abstract", "metadata"), "前作阅读级别有误")
        if scope == "online":
            need(p.get("query_id") in queries and queries[p["query_id"]]["status"] != "failed",
                 f"{p['id']} 缺少有效的发现或核验记录")
        local(root, p.get("note"))
    active = array(data, "selected")
    need(all(isinstance(x, str) and x in cards for x in active)
         and len(set(active)) == len(active), "主选编号有误或重复")
    states = {"selected", "reserve", "covered", "merged", "infeasible", "parked"}
    study = data.get("study_type", "general")
    need(study in ("general", "physics"), "研究类型有误")
    hypotheses = set()
    for c in cards.values():
        words(c, "question lens mechanism prediction status reason")
        cid = c["id"]
        need(c["status"] in states and ((cid in active) == (c["status"] == "selected")),
             f"{cid} 状态与主选名单不符")
        if c["status"] == "merged":
            dest = c.get("merged_into")
            need(dest in cards and cards[dest]["status"] != "merged", f"{cid} 合并关系无效")
        else:
            key = tuple(" ".join(c[field].casefold().split()) for field in ("mechanism", "prediction"))
            need(key not in hypotheses, f"{cid} 与已有候选的机制和预测完全相同，请检查合并")
            hypotheses.add(key)
        if c["status"] == "infeasible":
            words(c, "constraint_evidence")
        if c["status"] in ("covered", "selected", "reserve"):
            p = papers.get(c.get("prior"))
            need(p is not None and p["level"] != "metadata", f"{cid} 需要可定位的前作")
            words(c, "comparison")
            if c["status"] in ("covered", "selected"):
                need(p["level"] == "original", f"{cid} 缺少可核决定性原文")
        if c["status"] in ("selected", "reserve"):
            words(c, "baseline rival observable falsifier resources value next")
        if c["status"] == "selected":
            if study == "physics" or "physical_model" in c:
                model = c.get("physical_model")
                need(isinstance(model, dict), f"{cid} 缺少物理最小模型")
                words(model, "model conventions assumptions derivation limit_check analytic_next numerical_next")
                ledger = array(model, "claims")
                need(bool(ledger), f"{cid} 缺少物理主张台账")
                for entry in ledger:
                    words(entry, "statement basis status")
                    need(entry["status"] in ("established", "verified_numerically", "plausible",
                                             "conjecture", "unknown"), "物理主张证据类别有误")
            p = c.get("pilot")
            need(isinstance(p, dict), f"{cid} 缺少验证记录")
            if p.get("status") == "run":
                words(p, "protocol protocol_sha256 result result_sha256 observation implication limits")
                need(digest(local(root, p["protocol"])) == p["protocol_sha256"], f"{cid} 预设判据已变")
                need(digest(local(root, p["result"])) == p["result_sha256"], f"{cid} 试算结果文件已变")
                need(p.get("signal") in ("positive", "negative", "inconclusive", "informative_null"),
                     f"{cid} 未给出试算类别")
            else:
                need(p.get("status") == "unavailable", f"{cid} 试算状态有误")
                words(p, "reason alternative")
    need(data.get("decision") in ("shortlist", "no_viable", "partial"), "缺少最终决定")
    if data["decision"] == "shortlist":
        need(len(active) >= target, "主选少于用户要求，须补查、继续发散或说明限度")
        need(len(hypotheses) >= 2 or bool(str(data.get("narrow_reason") or "").strip()),
             "只有一个机制，请具体解释限制或探索其他机制")
    if data["decision"] == "no_viable":
        need(not active and all(c["status"] in ("covered", "merged", "infeasible") for c in cards.values()),
             "仍有可行或未决题目，与无可行项矛盾")
    review = data.get("review")
    need(isinstance(review, dict), "须说明反方检查")
    words(review, "mode attack answer trace")
    need(review["mode"] in ("self", "fresh_same_family", "different_family", "human"), "复核身份有误")
    local(root, review["trace"])
    if review["mode"] != "self":
        words(review, "reviewer")
    rounds = array(data, "rounds")
    need(bool(rounds), "缺少改变或维持选择的轮次记录")
    for row in rounds:
        words(row, "trigger evidence decision change")
    for match in data.get("pairs", []):
        words(match, "left right choice basis reversal")
        left, right = match["left"], match["right"]
        need(left in cards and right in cards and left != right, "成对比较的候选无效")
        need(match["choice"] in (left, right, "tie"), "比较结果不在本场候选内")
    return cards


def render(data, cards):
    lines = ["# 选题交接", "", data["direction"], "", data["constraints"], "",
             f"检索范围 `{data['scope']}`。反方检查方式 `{data['review']['mode']}`。", ""]
    papers = {p["id"]: p for p in data["papers"]}
    for cid in data["selected"]:
        c = cards[cid]
        p = papers[c["prior"]]
        lines.extend([f"## {cid}　{c['question']}", "", c["value"], "",
                      f"- 机制及预测　{c['mechanism']}。{c['prediction']}",
                      f"- 已有前作　{p['citation']}，{p['locator']}。{c['comparison']}。来源 {p['source']}",
                      f"- 竞争解释及对照　{c['rival']}。{c['baseline']}",
                      f"- 判别与资源　{c['observable']}。{c['falsifier']}。{c['resources']}",
                      f"- 首项行动　{c['next']}", ""])
        pilot = c["pilot"]
        if pilot["status"] == "run":
            lines.extend([f"试算　{pilot['observation']}。{pilot['implication']}。{pilot['limits']}", ""])
        else:
            lines.extend([f"未执行试算　{pilot['reason']}。{pilot['alternative']}", ""])
        if "physical_model" in c:
            model = c["physical_model"]
            lines.extend([f"模型　{model['model']}。{model['conventions']}。{model['assumptions']}",
                          f"校验　{model['derivation']}。{model['limit_check']}", "",
                          f"解析工作　{model['analytic_next']}", f"数值工作　{model['numerical_next']}", ""])
            for item in model["claims"]:
                lines.append(f"- {item['status']}　{item['statement']}。{item['basis']}")
            lines.append("")
    lines.extend(["## 取舍", ""])
    for c in cards.values():
        lines.append(f"- {c['id']}　{c['question']}　{c['status']}　{c['reason']}")
    lines.extend(["", "## 反方与重排", "", data["review"]["attack"], "", data["review"]["answer"], ""])
    for row in data["rounds"]:
        lines.append(f"- {row['trigger']}。{row['evidence']}。{row['decision']}。{row['change']}")
    for match in data.get("pairs", []):
        lines.append(f"- {match['left']} 与 {match['right']}　{match['choice']}。{match['basis']}。{match['reversal']}")
    lines.extend(["", "## 停止依据与下一步", "", data["stop"], "", data["next_step"]])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("init", "check", "handoff", "hash"))
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    file = args.file.resolve()
    if args.action == "hash":
        print(digest(file))
        return
    if args.action == "init":
        file.parent.mkdir(parents=True, exist_ok=True)
        with file.open("x", encoding="utf-8") as f:
            json.dump(dict(version=1, direction="", constraints="", scope="online", target=1,
                           queries=[], papers=[], ideas=[], selected=[], decision="", review={},
                           rounds=[], stop="", next_step=""), f, ensure_ascii=False, indent=2)
        return
    data = json.loads(file.read_text(encoding="utf-8-sig"))
    cards = check(data, file.parent)
    if args.action == "handoff":
        print(render(data, cards))
    else:
        print(f"{data['decision']} | {len(cards)} 个候选 | {len(data['selected'])} 个主选 | "
              f"复核 {data['review']['mode']} | 范围 {data['scope']}")
    if data["decision"] == "partial":
        sys.exit(1)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        main()
    except (ValueError, TypeError, KeyError, OSError, AttributeError) as error:
        sys.exit(f"档案未通过检查　{error}")
