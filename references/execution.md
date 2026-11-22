# 实际运行和交接

`<skill>` 表示本技能目录，`<case>` 是这次研究的工作目录。使用 Python 3.9 或以上，无第三方库。

1. 运行 `python "<skill>/scripts/topic_run.py" init "<case>/topic.json"` 创建空档案。已有档案继续使用，初始化不会覆盖文件。先填写 direction、constraints、scope（online 或 provided_only）和用户需要交付的主选数 target，用户没指定时取 1。
2. 执行实际检索。可用学术检索服务、官方索引、专业学会和预印本库。有同项目的 research-idea-novelty-check 时，可直接运行其 `scripts/search_papers.py search --public-query "公开术语" --source both --limit 10 --output "<case>/search.json"`。独立部署时照常访问可用学术服务，保存其返回或可复查的结果摘录。两个库共用一条查询词时只算一种问法。遇到限流保留失败并尝试替代索引。按 DOI、版本及研究身份去重，区分结果的总数、实际看到的篇数和最终纳入数。
3. 按下表逐步记录。入围候选需给出第一项能检验竞争解释的行动。用选择前已存在的文件记录试算方案，运行 `python "<skill>/scripts/topic_run.py" hash "<case>/protocol.md"` 记下 SHA-256。再执行小型试算，保存脚本、参数、原始结果与结果指纹。得到结果后若改变指标，保留原先记录，在新一轮另列探索分析。比对指纹只能发现内容变化，不能证明文件创建顺序。
4. 运行 `python "<skill>/scripts/topic_run.py" check "<case>/topic.json"`。字段或证据引用无效时按错误修复或降低结论。最后运行 `python "<skill>/scripts/topic_run.py" handoff "<case>/topic.json"` 生成提纲，并结合原文、资源和取舍写成面向研究者的定题卡。子命令输出为 UTF-8。已有记录若由旧版技能产生，按表补入字段，保留原日期。程序检查的是档案结构、附件及编号；来源是否独立、预测是否可区分和证据是否读对，仍须核原文和方法。

| 记录 | 字段与约定 |
|---|---|
| queries 数组 | 每行 id、source、query、date（YYYY-MM-DD）、operation（search、lookup 或 citation）、status（ok、partial、failed）、trace（实际返回的相对路径）。ok 时 screened 为实际筛读数，可为零。其他状态填写 reason。lookup 和 citation 不能充当跨库主题检索；某索引没有结果或者结果无法读取，不计入已筛读的来源。只有本地材料时 scope=provided_only，填写 scope_reason。 |
| papers 数组 | id、citation、source（官方链接或用户提供文件）、locator（页、节、图或式）、observation、level（original、abstract、metadata）、note（证据摘录的相对路径）。联网情况下 query_id 指到索引或追引记录。保留识别论文与读懂证据的差别。 |
| ideas 数组 | 每条均填 id、question、lens、mechanism、prediction、status、reason。status 取 selected、reserve、covered、merged、infeasible 或 parked。merged 填 merged_into 指向保留的卡。infeasible 填 constraint_evidence 说明真实约束。covered、selected 和 reserve 都要填 prior（文献编号）与 comparison，前两类需要读到该关键原文。 |
| 可推进题目 | selected 与 reserve 的卡上再填 baseline（朴素对照）、rival（竞争解释）、observable（测什么）、falsifier（什么观察能推翻）、resources、value、next。selected 数组列出排名后的主选编号。主选卡含 pilot 对象。能试算时 status=run，填 protocol、protocol_sha256、result、result_sha256、observation、implication、limits 以及 signal（positive、negative、inconclusive 或 informative_null）；缺少执行条件时 status=unavailable，填具体 reason 和 alternative。 |
| 收敛 | review 含 mode（self、fresh_same_family、different_family、human）、attack、answer、trace。后三种写 reviewer，留实际调用或回执。rounds 数组每项含 trigger、evidence、decision、change，写清何种证据维持或改变了哪些候选。decision 取 shortlist、no_viable 或 partial。stop 写为何可结束，next_step 写下游拿到材料先做什么。只有一个非重复候选时用 narrow_reason 说明范围。 |

物理推导、仿真或复现的课题在档案根节点填 study_type=physics，逐个主选填 physical_model。候选难分排序时填写 pairs 数组。字段、证据类别与成对比较方法见[模型与候选改进](refinement.md)。未指定类型的旧档案按通用研究读取。

交付少于用户指定数量时，先补做独立分支和反例搜索。仍不足时报告真实条数和原因，decision=partial。完全没有可行项时可给 no_viable，并列对每个分支的证据。check 对结构合格的 shortlist 或 no_viable 返回 0；partial 或档案有错返回非零。程序没有为近邻搜不到或自评高分设置“首创”标签。
