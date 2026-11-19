import json,pathlib,collections
P=pathlib.Path(__file__).resolve().parent
ids=['3a122ee7ff513956','e531cded0108b6c3','0573fc312656e95a']
lines=['# 01a 试点报告','', '状态：3 个试点完成并通过结构校验；停在人工金标准修订之前。未执行 01c、批量标注、独立验证或 predictable。所有原始输入保持不变。','', '从原 fine 文件筛出 32 个视频，清单见 `video_list_placeholder.txt`。选择烹饪 `3a122ee7ff513956`、手工 `e531cded0108b6c3`、占位符最多的 `0573fc312656e95a`（77 个）。共保留 128 个 fine step 和全部原始边界，重写 127 个有效区间描述，1 个越界区间描述为 null。','', '画面证据：先看每 2 秒一帧的全片概览，再看各 step 外扩 0.5 秒的密集接触表（3 fps；不足 1 秒用 15 fps），并对每段结束前的原生帧核对左右手。文件在 `frames/<id>/overview_*`、`step_*/dense_*`、`ends/*.jpg` 和 `fullends_*.jpg`。末帧脚本从头解码、按原生 15 fps 帧号选择，drawtext 保留原始 PTS；密集图的 fps 在 drawtext 前，时间显示采样网格，内容与真实时间误差至多约一采样间隔。边界处以原生末帧为准。','', '已排除的抽帧显示问题：初版末帧接触表把 448×592/596 的竖幅图按横幅高度排版，造成下部手被覆盖；`fullends_*.jpg` 已保持完整比例。旧 `ends_*.jpg` / `verified_ends_*.jpg` 仅为调试遗留，勿用；单张 `ends/` 与 `fullends_` 才是核对依据。密集目录可能有早期命令残留的末页，只使用画面烧录时间在该 step 外扩区间内的页。','', '结构校验：运行 `python validate.py`，结果见 `validation_results.json`，3 个视频 errors 均为空。检查包括数量、原边界、old_summary、词表、字数、字段枚举、越界空值、coarse 连续覆盖与对齐、所有转移的脚本重算。可审查警告保留在结果中。','']
alls=collections.Counter();allc=collections.Counter();ambn=bn=0
for v in ids:
 d=json.loads((P/'videos'/f'{v}.json').read_text());f=d['fine'];c=d['coarse'];s=collections.Counter(x['transition_in'] for x in f);ct=collections.Counter(x['transition_in'] for x in c);alls.update(s);allc.update(ct)
 amb=[(i,x) for i,x in enumerate(f) if x['ambiguous']];boundary=[(i,x) for i,x in enumerate(f) if x['boundary_note']];ambn+=len(amb);bn+=len(boundary)
 lines += [f'## {v}', '', f"Goal: **{d['goal']['title']}**",'',d['goal']['description'],'',f"Final state: {d['goal']['final_state']}",'',f"真实时长 {d['duration']:.3f}s；{len(f)} fine、{len(c)} coarse；ambiguous {len(amb)}，boundary_note {len(boundary)}。",'', '| 层级 | STRONG | WEAK | NONE | 首段 null |','|---|---:|---:|---:|---:|']
 for name,z in [('step',s),('subtask',ct)]:lines.append(f"| {name} | {z['STRONG']} | {z['WEAK']} | {z['NONE']} | {z[None]} |")
 lines+=['','Subtask（fine index 为从 0 开始、双闭区间）：','']
 for i,x in enumerate(c):lines.append(f"- #{i} [{x['start']:.2f}, {x['end']:.2f}]s fine {x['fine_index_range']}: {x['instruction']} — {x['description']}")
 lines+=['','前 15 个 step（手工视频共 8 个）：','']
 for i,x in enumerate(f[:15]):lines.append(f"- #{i} [{x['start']:.2f}, {x['end']:.2f}]s: {x['summary']}")
 lines+=['','Ambiguous：','']
 for i,x in amb:lines.append(f"- #{i}: {x['boundary_note'] or x['notes']}")
 if not amb:lines.append('无。')
 lines+=['','Boundary notes：','']
 for i,x in boundary:lines.append(f"- #{i}: {x['boundary_note']}")
 lines+=['','视频级观察：'+d['notes'],'']
lines+=['## 规则难点与本次处理','', '- 原始边界保留优先。手工视频最后一个 step 从 46.83 到 173s，跨越剪胶带、喷涂、揭模和描边；无法在这些画面目标之间建立与 fine 对齐的 coarse 边界，因此仅给 2 个 coarse，并在 boundary_note 中具体列出动作，交人工决定如何形成金标准。未添加漏掉的尾部 step。', '- 原始细分有时把同一个持续动作切成多段。保持边界并重复同一句真实指令，在 boundary_note 中注明连续动作，不为制造不同描述而编造动作变化。', '- 手持字段是结束前最后一个原生帧上的抓持状态；按包装袋/工具命名，不把已放在墙里的锚栓继续算作手持。接触固定墙面、柜台或微波炉门不算拿着这些固定物体。抓住并支撑固定挂钩仍算持有。', '- 同一只手可同时抓住挂钩和螺丝刀，因此 in_hand_at_end 使用多个物体。无法读出钻头直径，所有相似钻头统一 drill bit，未按预期推断尺寸。', '- 祈使句使用必要的新动词，如 pull、spray、drill、loosen、withdraw，未强行替换成不准确的建议词表动词。', '- 烹饪加热等待和品尝暂按 idle；品尝可能被视为检查成品，应由人工在试点统一。盖住调味罐和放下盐瓶仍是任务交互，标 action。', '- 严格越界：烹饪 #42 end=124.7 > ffprobe=124.667，尽管仅差 0.033s，仍不描述整段并设置 beyond_video_end=true，未裁剪边界。此段 type 暂为 idle，ambiguous=true、low；人工作金标准时应明确微小取整误差的策略。', '- 转移只按下一段 object/tool 是否在上一段持有列表内计算，target 不参与。命名严格词表一致，不手动改变结果；因此松散食材从袋中倒出的 STRONG 往往依赖 tool=bag。', '- 失败/返工直接按画面写：窗帘挂钩在试装后仍未安装，继续用螺丝刀压锚栓并换钻头扩大孔；与一次性安装的预期不同，已记录 differs_from_expectation。','',f'总计 ambiguous={ambn}，boundary_note={bn}。','', '| 层级合计 | STRONG | WEAK | NONE | 首段 null |','|---|---:|---:|---:|---:|']
for name,z in [('step',alls),('subtask',allc)]:lines.append(f"| {name} | {z['STRONG']} | {z['WEAK']} | {z['NONE']} | {z[None]} |")
lines+=['','下一步停点：用户使用第 02 步编辑器逐字段修订 3 个视频，并保存 `gold/<id>.json`。此时再执行 01c 比较和提炼规范；本轮未生成 guideline，也未将 agent 输出当作金标准。','']
(P/'pilot_report.md').write_text('\n'.join(lines))
print('report written',ambn,bn)
