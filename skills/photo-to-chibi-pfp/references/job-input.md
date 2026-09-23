# 本地任务准备接口

辅助脚本不调用模型。Agent负责看图、补齐观察、调用内置生图并检查实际产物。

## 命令

- `styles`：列出九种画风及别名，无需Pillow。
- `template --out`：写入新空白brief；`--style`默认pop_mart，`--deliverable`默认nine_grid。模板按交付切换series/preserve；已存在文件不覆盖。无需Pillow。
- `prepare --brief --out`：校验并写入job.json及提示词；输入均为绝对路径，输出使用新目录。
- `inspect --image`：输出格式、尺寸与透明度事实，不判断相似度或风格。

各命令可用`--help`查看参数。所有路径支持空格；在Windows中兼容附件形如`/C:/`的多余前导斜杠，实际读取前仍验证绝对路径和文件。相对路径不猜测。图片仅支持静态JPEG、PNG、WebP；人物与参考输入最短边至少64像素且不能全透明。inspect可检查24像素的小尺寸最终产物。

## brief重点字段

| 字段 | 用途 |
| --- | --- |
| photo_path | 必需，当前人物照片，决定脸部与发型 |
| style_path | 可选，材质/笔触/画风参考，空值用null |
| design_path | 可选，已选穿搭/道具/九格顺序参考，只能配合series或redesign |
| style_id | 缺省pop_mart，支持styles列出的别名 |
| deliverable | 缺省nine_grid；可选full_body、avatar、both |
| outfit_mode | nine_grid缺省series；其它缺省preserve；单套换装用redesign |
| outfit_variants | series必需，九项互不重复name/design，Agent看图或设计后填写 |
| outfit_design | redesign必需，明确单套新穿搭 |
| face_profile | 六组脸部关系观察，不得编造精确测量 |
| identity_anchors | 3–8项辨识特征，避免把旧衣服写成新换装中不可变的人物特征 |
| visible_outfit | 记录原照事实；series/redesign中作为背景信息，不压过新设计 |
| source_view | full_body或half_body |
| allow_lower_body_design | 半身转全身或九宫格所需；须JSON布尔值 |
| inferred_design | 记录原照未见部分的设计补全，禁止冒充原照还原 |
| background | auto跟随画风；显式dark/light/transparent优先于风格与参考图背景 |

图片索引由脚本按photo→style（若有）→design（若有）建立，读取任务的input_images，不硬编码“第三张一定是什么”。both的衍生母版仅在检查通过后追加为最后一张。

## 状态与兼容

job schema_version=5，新增可选design_path、设计参考metadata和输入角色。旧brief不含design_path仍可用，明确的单张/头像交付保持。空模板仍需Agent补齐，脚本不会虚构人物事实。

prepare成功仅代表prepared、generation_performed=false；review_state仍为not_checked。错误使用非零退出码与JSON说明。未装Pillow时图像命令清楚报告依赖缺失，菜单与模板仍可使用。格式校验与字符串去重不能证明九套设计在视觉上充分不同，最终逐格看图。
