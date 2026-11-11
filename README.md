# 花小烙skill

面向中文知识漫画的可移植skill。把参考视频里能观察的表达拆成证据，再用来做原创选题、口播、小剧场、逐状态画稿和制作交付。

核心是让知识关系成为角色遇到的事情。选题提供一个能回答的问题，文案沿着问题推进；夸张放大目标、条件或后果，最后回到可核实解释；姿态与表情真的发生变化，持帧给观众理解的时间。

目前停止制作视频。保留[视频成品约束](references/motion-contract.md)，约定有限动画、竖版中的横向舞台、真实动作状态、触发顺序、图层接触、字幕与用户自行配音/BGM。这个仓库没有视频渲染器。

## 在新对话使用

将整个目录安装到你的skills目录，目录名保持`huaxiaolao-skill`。支持Codex的环境可放进用户的`.codex/skills/`目录。然后在新对话明确调用

```text
使用 $huaxiaolao-skill。先读本包证据和复盘。
这次讲[知识问题]，面向[观众]，沿用附件角色。
先给三种入口与取舍，再完成口播和关键视觉状态计划。
只做方案，不作画、不编码视频。事实有疑问先查证。
```

换成其他AI时，把完整目录提供给它，要求从[SKILL.md](SKILL.md)开始，并按其中链接按需读取。涉及画风还要打开证据图片。不能只复制SKILL.md丢掉references、assets和scripts。没有本地读图能力时要明确限制，不能声称看过原帧。

需要实际画稿时，将范围改为“生成状态图片和修改记录，交付透明分层与素材清单”；需要局部改稿时只给当前稿与修改要求，不必重跑所有阶段。图像生成能力由所用AI环境提供，本包没有捆绑模型、API密钥或付费工具。

## 目录

| 路径 | 作用 |
|---|---|
| [SKILL.md](SKILL.md) | 执行入口与范围判断 |
| [研究案例](references/research-cases.md)与[证据索引](references/evidence/INDEX.md) | 三个样本、两条深拆、23个精选证据文件与研究限制 |
| [选题与写作](references/topic-and-writing.md) | 受众收益、问题链、事实核验、正文与标题 |
| [画面与表达](references/art-and-expression.md) | 外形、线条、色块、夸张、知识与戏剧场景统一 |
| [逐状态画稿](references/drawing-states.md) | 保持/变化、实际改画、提示词、图层和接触 |
| [复盘与续接](references/lessons-and-continuity.md) | 纠错、失败表现与版本状态 |
| [字段契约](references/plan-contract.md)、[计划样例](assets/episode-plan.example.json)、[交接模板](assets/handoff.template.md) | 可复制的计划和续接材料 |
| [回测记录](tests/RESULTS.md) | 实测范围、结果和未证明的事项 |

## 检查方法

需要Python 3.10或更高版本；本包脚本只用标准库。下面的`python`指环境内实际可用的解释器；可以替换为`python3`、`py -3`或解释器完整路径。Windows的商店占位命令不代表Python已运行，先用`--version`确认。无需为此改写脚本或安装图像/视频依赖。在本目录运行

```shell
python scripts/check_package.py
python scripts/check_plan.py assets/episode-plan.example.json --phase handoff
python -m unittest discover -s tests -v
```

实际制作计划的图片到齐后，再运行`python scripts/check_plan.py episode-plan.json --phase assets`。示例所有图片都标为planned，不能通过assets阶段，这是预期行为。机器检查仅验证可计算关系，不评价科学真伪、画风、趣味和艺术认可。

## 研究边界

参考作者为画渣花小烙。附带图片只作有署名的研究证据，不是原创生产资产，不表示得到作者授权。保留原片链接与SHA256，不包含原片视频或音轨。研究中没听原片声音，历史逐帧覆盖也不等于全片逐输出帧人工审阅。

当前可复现的是创作决策、画稿规格、交付结构和检查办法。生成画面会受模型与输入参考影响，不能保证像素一致；历史袋熊试做没有被用户确认画风通过，也没有用受众数据证明这些办法能获得高热度。
