# 候选很接近时怎样选择，涉及物理模型时怎样交接

## 让三种立场改进同一组题目

从三条互不依赖的主线出发，让一人提出机理突破，一人只按现有设备和周期改写，一人寻找能够推翻预测的最简单解释。各自先写，再汇合阅读。先从真实论文中画“困难—解法”的多对多表。某行空白先换术语检索，某列已经充满时问哪一项硬约束使现成方案失效。用上一轮最相关的两条成功或失败记录检查是否重复走同一条路。每次改写都保留父题编号，并写清是补文献、修逻辑、组合、减变量还是依据新证据改题。相同科学问题重复措辞不计为新分支。[EvoScientist 选题入口](https://github.com/EvoScientist/EvoSkills/blob/85ad685d1df5ed1d7fe641564d04bb8a3dec8f28/skills/research-ideation/SKILL.md#L52-L154) · [困难与解法的映射](https://github.com/EvoScientist/EvoSkills/blob/85ad685d1df5ed1d7fe641564d04bb8a3dec8f28/skills/research-ideation/references/literature-tree.md)

若剩余主线难分高下，对相近的两条作成对比较。固定四项标准，即已知差别、资源可行性、结果对用户问题的价值和是否足以开做，分别给证据与理由。三条入围主线可以每对比较一次；有平局要说明哪项观察会打破平局。原版用初始 Elo 1500、K=32 累积分数并保留三条主线。需要复现这套排序时按原指南记录出场顺序、四项原始分数与同分规则。单人自评或仅有两条可行题目时，保留成对理由和反转条件即可。比较排序用于分配有限的试算，不能据此排除某项新颖性。将每次比较写入 pairs，填 left、right、choice（胜出编号或 tie）、basis 和 reversal。需要与导师讨论时，再交给方案阶段展开六部分提案。[成对评分与平局](https://github.com/EvoScientist/EvoSkills/blob/85ad685d1df5ed1d7fe641564d04bb8a3dec8f28/skills/research-ideation/references/elo-ranking-guide.md) · [后续提案结构](https://github.com/EvoScientist/EvoSkills/blob/85ad685d1df5ed1d7fe641564d04bb8a3dec8f28/skills/research-ideation/references/proposal-extension.md)

## 把物理主选收窄到可复核的最小模型

在主选涉及物理推导、数值模拟或复现时，将 physical_model 放在候选卡内。写出简化系统、变量及单位/归一化、容易混淆的符号和显式假设；列出关键公式属于原文、自己推导或数值近似，给原文的公式号或推导文件。选择一条可独立计算的守恒量、极限解、对称性或解析反例，记录所用边界与数值误差。把解析极限和计算结果直接比较。若二者冲突，依次核符号、物理量定义、边界/初始条件、离散化及采样误差；保留冲突的原始结果，决定先回哪一步。对纯模拟题把明确的解析计划与后续数值计划交接。避免将预选阶段的玩具模型当作论文主结果。[物理探索入口](https://github.com/qjgoisz/physics-research-agent-kit/blob/ee2a4dffb76dd8916830cca72cee9800ca0c1274/skills/physics-research-explore/SKILL.md) · [原文、推导和复现核对](https://github.com/qjgoisz/physics-research-agent-kit/blob/ee2a4dffb76dd8916830cca72cee9800ca0c1274/skills/physics-research-explore/references/evidence-and-derivation.md)

physical_model 内填 model（最小模型）、conventions、assumptions、derivation（权威出处或本轮可读附件及位置）、limit_check、analytic_next、numerical_next。claims 数组每项填 statement、status、basis。status 取 established（已核推导或原文）、verified_numerically（可重跑计算）、plausible（有推理支持）、conjecture（有意提出的未验证猜想）或 unknown（不确定）。这五类只标各自主张的证据地位。只能证明基线在构造序列上失效，就把这项写成已证，把“真实海面会发生”留为猜想。把卡和证据文件一起交给后续阶段，读者能找到下一次推导、数值计算和可能的失败点。[人读的交接模板](https://github.com/qjgoisz/physics-research-agent-kit/blob/ee2a4dffb76dd8916830cca72cee9800ca0c1274/skills/physics-research-explore/assets/README.template.md) · [状态台账模板](https://github.com/qjgoisz/physics-research-agent-kit/blob/ee2a4dffb76dd8916830cca72cee9800ca0c1274/skills/physics-research-explore/assets/RESEARCH-STATE.template.md)
