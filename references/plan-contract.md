# 制作计划字段与检查器

综合交付才用这个结构。只改一句口播不必创建JSON。复制[示例](../assets/episode-plan.example.json)后替换内容，所有ID在各自类型内唯一，状态ID跨场唯一。

| 字段 | 含义 |
|---|---|
| schema_version | 当前为1 |
| project | title、audience、promise、comprehension_question；执行范围video_execution默认false |
| format | width、height、fps；layout为portrait-horizontal时，画布竖向，stage为内部横向矩形{x,y,width,height} |
| claims | id、statement、kind（fact/hypothesis/metaphor）、verification（verified/pending/fictional）、sources、limits。事实来源写url、locator、supports；数学推导可写kind=derivation、locator、supports、method，无需捏造外部链接 |
| voice_lines | id、text、claim_ids。只放实际朗读内容，制作注释不混入 |
| assets | id、path（相对计划文件）、kind、status（planned/generated/user_approved）、drawing_id。后者表示同一独立画稿，不同组合不能虚报重画张数 |
| scenes | id、duration_frames、knowledge_task、claim_ids、states |
| states | id、start_frame、end_frame、asset_ids、tag、change、hold、trigger_state_ids、voice_line_ids。区间为场内左闭右开，完整覆盖场景；tag选HOLD/POSE_SWAP/FACE_SWAP/DRAW_STEP/REVEAL/MOTION/SYMBOL/DIAGRAM |
| review | factual_status、style_status、user_approved、notes。计划通过和艺术认可分开写 |

同一状态可以组合多个素材，图层细节另加layers与anchors即可，不要求把所有东西切成一套僵硬字段。绘制进度用DRAW_STEP须真的有分阶段资产；计划里的标签不能证明已经画过。

执行`python scripts/check_plan.py episode-plan.json --phase plan`检查结构、引用、完整覆盖、触发先后和相对路径。pending事实与planned素材允许草案继续，但会提示。`--phase handoff`要求事实来源齐全；`--phase assets`还要求所有登记素材实际生成并存在于计划目录内部。路径不允许绝对路径或逃出计划目录。

检查器不核验来源内容的科学真伪，不识别画风、笑点、真实透明通道或动作语义，不校验音画同步，不证明图片或视频被观看，也不替用户盖艺术通过章。对照片或PNG仍需实际打开检查。纯方案示例没有实际画稿，不能通过assets阶段。
