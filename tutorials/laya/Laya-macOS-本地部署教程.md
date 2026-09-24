# Laya 本地部署教程｜macOS 版

目标：在 Mac 本地运行 Laya，通过本地 MCP 供 Codex 调用。主线是 Apple Silicon 的 MPS；另附 CPU 和 Intel Mac 兼容性检查。

版本：v1｜资料核对：2026-09-24\
验证范围：官方资料核对、教程代码静态检查。本次没有 Mac 实机，未执行 macOS 安装、MPS 推理或 Codex 实际调用。

## 先确认你的 Mac

| 条件 | 路线与边界 |
|---|---|
| Apple Silicon：M 系列芯片 | 原生 arm64 Python，优先尝试 MPS |
| Apple Silicon，MPS 不可用 | 明确选择 CPU，性能另测 |
| Intel Mac | 仅做 CPU 兼容性检查；当前依赖可能无可安装的二进制包，不承诺最新版可用 |
| 希望用 CUDA | 不适用本教程；Mac 使用 MPS 或 CPU |

核对时 Apple 安装页列出 Apple Silicon、macOS 14.0+、Python 3.10+ 和 Xcode 命令行工具；这些要求对应该页所述 PyTorch 版本，实际仍以安装版本为准。[Apple 官方说明](https://developer.apple.com/metal/pytorch/)

建议优先 16GB 以上统一内存、预留 10GB 以上磁盘。这是余量建议，不是官方最低配置。8GB 机器先用单模型和短输入实测，模型文件大小不能等同推理内存峰值。

本地 Laya 无需 Jev Key；安装和首次下载需要联网。接入不会把 Codex 主模型变成本地模型。

## 1．准备原生 Python

打开“终端”：

~~~bash
sw_vers
uname -m
python3 --version
python3 -c 'import sys, platform, struct; print(sys.executable); print(platform.machine()); assert sys.version_info >= (3,10); assert struct.calcsize("P") == 8'
~~~

- M 系列预期 arm64。若 Python 显示 x86_64，检查 Rosetta，先换原生终端和 Python。
- Intel 显示 x86_64 正常，使用 CPU 兼容性分支。
- 没有合适 Python 时，从 [Python 官方 macOS 下载页](https://www.python.org/downloads/macos/)安装原生兼容版本，建议 3.11 或 3.12。重新打开终端后复查，不修改系统解释器。

检查命令行工具：

~~~bash
xcode-select -p
~~~

没有安装时再执行：

~~~bash
xcode-select --install
~~~

安装完成再继续。已有 Homebrew 的读者也可使用自己维护的原生 Python，本教程不要求额外安装 Homebrew。

## 2．创建独立环境

在当前用户主目录创建 Laya 文件夹。其他电脑的真实用户名无法预知，因此由系统解析并打印完整路径，不照抄虚构的 /Users/用户名 路径。

在同一个终端逐块执行；任何一步报错就停止，不继续下一块。

~~~bash
layaRoot="$HOME/Laya"
if [ -e "$layaRoot" ]; then
  printf '目录已存在，请先检查旧部署或修改目录：%s\n' "$layaRoot"
else
  mkdir -p "$layaRoot"
  python3 -m venv "$layaRoot/.venv"
fi
~~~

目录原先存在时，不继续使用未知环境；改用新版本目录，重跑本节。

~~~bash
layaPython="$layaRoot/.venv/bin/python"
"$layaPython" -m pip install --upgrade pip
printf '部署目录：%s\n专用 Python：%s\n' "$layaRoot" "$layaPython"
~~~

无需激活环境，不使用 sudo pip。新开终端需要恢复这些变量和下文环境变量。

## 3．安装 PyTorch 和 Laya

### A．Apple Silicon

~~~bash
"$layaPython" -m pip install torch
"$layaPython" -m pip install 'laya[mcp,serve]'
"$layaPython" -m pip check
"$layaPython" -I -c 'import laya; import laya.mcp.server; from importlib.metadata import version; print("laya", version("laya"))'
~~~

每行成功再执行下一行。首次不使用 nightly、编译加速、TileLang 或转换权重，先确认普通推理。

尝试 MPS 并运行真实张量运算：

~~~bash
export LAYA_DEVICE=mps
"$layaPython" -c 'import torch; print(torch.__version__); print("built:", torch.backends.mps.is_built()); print("available:", torch.backends.mps.is_available()); assert torch.backends.mps.is_available(), "MPS unavailable"; print(torch.ones(1, device="mps"))'
~~~

失败时先查系统版本、Python 架构和 PyTorch。决定先用 CPU 时明确执行：

~~~bash
export LAYA_DEVICE=cpu
"$layaPython" -c 'import torch; print(torch.__version__); print(torch.ones(1))'
~~~

这属于 CPU 部署，不能标记为 MPS 成功。

### B．Intel Mac：先检验依赖

此分支替代 Apple Silicon 安装分支。使用新虚拟环境，预检：

~~~bash
"$layaPython" -m pip install --dry-run --only-binary=:all: 'laya[mcp,serve]'
~~~

No matching distribution 或依赖无法解析时，到这里停止。当前 Python/macOS/架构没有通过本路线兼容性检查；不要随意降级到很旧的 PyTorch，也不要称为部署成功。

仅预检成功后尝试：

~~~bash
"$layaPython" -m pip install --only-binary=:all: 'laya[mcp,serve]'
"$layaPython" -m pip check
"$layaPython" -I -c 'import torch, laya; import laya.mcp.server; print(torch.__version__); print(torch.ones(1))'
export LAYA_DEVICE=cpu
~~~

依赖可解析不证明模型能运行。仍需通过后续真实推理。若不兼容，另行评估其他本地运行时或设备；不算本教程路线成功。

## 4．设置缓存并保存版本

~~~bash
export LAYA_ROOT="$layaRoot"
export HF_HOME="$layaRoot/model-cache"
export USE_TF=0
export PYTHONUTF8=1
unset PYTORCH_ENABLE_MPS_FALLBACK
"$layaPython" -m pip freeze > "$layaRoot/requirements-$(date +%Y%m%d-%H%M%S).txt"
~~~

默认不启用 MPS 算子级 CPU 回退，避免隐藏执行设备；仍需检查模型自己的回退。

核对时作者主分支标为 0.3.17，但源码、PyPI 和权重版本不同。保存实际环境，不宣称未测试组合稳定。[包信息](https://pypi.org/project/laya/)

## 5．下载模型并测试真实推理

以下整块命令写入测试脚本，只请求多语言 checkpoint。首次需联网下载。

~~~bash
cat > "$layaRoot/smoke_test.py" <<'PY'
import json
import os
import time
from importlib.metadata import version
from pathlib import Path
import laya
import torch

requested = os.environ["LAYA_DEVICE"]
if requested == "cuda" and not torch.cuda.is_available():
    raise SystemExit("CUDA unavailable; stop and fix the GPU environment.")
if requested == "mps" and not torch.backends.mps.is_available():
    raise SystemExit("MPS unavailable; stop or explicitly choose CPU.")
agent = laya.load(
    "convaiinnovations/laya", subfolder="multilingual", device=requested,
)
questions = {
    "category": {
        "type": "choice",
        "instructions": "根据客户留言选择最合适的服务类别。",
        "criteria": {
            "presales": "购买前咨询价格、规格或库存",
            "aftersales": "已收货后的故障、退货或退款",
            "other": "与购买及售后无关",
        },
    },
    "refund": {"type": "noul", "instructions": "客户明确要求退款。"},
}
cases = [
    ("收到的商品无法开机，我要求退货退款。", "aftersales"),
    ("还没下单，请问这款有哪些颜色？", "presales"),
    ("祝你周末愉快。", "other"),
]
rows = []
for text, expected in cases:
    if requested == "cuda":
        torch.cuda.synchronize()
    elif requested == "mps":
        torch.mps.synchronize()
    start = time.perf_counter()
    result = agent.predict({"text": text}, questions)
    if requested == "cuda":
        torch.cuda.synchronize()
    elif requested == "mps":
        torch.mps.synchronize()
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    actual = agent.device.type
    if actual != requested:
        raise RuntimeError(f"Device changed: requested={requested}, actual={actual}")
    answers = result["answers"]
    selected = answers["category"]["choice"]
    assert selected in questions["category"]["criteria"]
    probabilities = answers["category"]["probabilities"]
    assert set(probabilities) == set(questions["category"]["criteria"])
    assert all(0 <= p <= 1 for p in probabilities.values())
    assert abs(sum(probabilities.values()) - 1) < 0.01
    assert 0 <= answers["refund"]["noul"] <= 1
    rows.append({
        "text": text, "expected": expected, "choice": selected,
        "matches_expected": selected == expected,
        "actual_device": actual, "elapsed_ms": elapsed_ms, "answers": answers,
    })
report = {
    "laya_version": version("laya"), "torch_version": torch.__version__,
    "requested_device": requested, "actual_device": agent.device.type,
    "sample_matches": sum(row["matches_expected"] for row in rows),
    "sample_count": len(rows), "results": rows,
    "note": "Three smoke cases are not a production accuracy benchmark.",
}
output = Path(os.environ["LAYA_ROOT"]) / f"smoke-{time.time_ns()}.json"
output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
print("Saved:", output.resolve())
PY
"$layaPython" "$layaRoot/smoke_test.py"
~~~

检查结果：

- actual_device 与 requested_device 一致；请求 MPS/CUDA 却退回 CPU 会报错。
- 三个场景都有分类、合法概率和耗时，并保存带时间编号的 JSON 报告。
- sample_matches 不是 3 时，先检查基础误判和模型选择。
- 三个例子不是准确率基准；首条请求也可能含预热。输出耗时不含模型加载，不代表 Codex 端到端延迟。

MPS=True 只说明后端可用，不能证明模型实际在 GPU 上运行。[Laya 设备逻辑](https://github.com/NandhaKishorM/laya/blob/main/laya/agent.py)

## 6．接入 Codex

~~~bash
codex --version
codex mcp list
~~~

找不到命令时，按 [Codex CLI 官方说明](https://developers.openai.com/codex/cli/)安装或配置命令行入口。不要假设桌面安装一定已配置终端 PATH。

以下会新增持久 MCP 配置。已有 laya 时先运行 codex mcp get laya 查看并保留旧配置，不重复添加。

备份实际配置，读取 CODEX_HOME 但不修改它：

~~~bash
if [ -n "$CODEX_HOME" ]; then
  layaCodexDir="$CODEX_HOME"
else
  layaCodexDir="$HOME/.codex"
fi
layaCodexConfig="$layaCodexDir/config.toml"
if [ -f "$layaCodexConfig" ]; then
  cp "$layaCodexConfig" "$layaCodexConfig.before-laya-$(date +%Y%m%d-%H%M%S).bak"
fi
printf '配置位置：%s\n' "$layaCodexConfig"
~~~

确认没有同名服务后注册：

~~~bash
codex mcp add laya \
  --env "LAYA_DEVICE=$LAYA_DEVICE" \
  --env "HF_HOME=$HF_HOME" \
  --env LAYA_PRELOAD=0 \
  --env LAYA_MODELS=multilingual \
  --env USE_TF=0 \
  --env PYTHONUTF8=1 \
  --env PYTORCH_ENABLE_MPS_FALLBACK=0 \
  -- "$layaPython" -m laya.mcp.server
codex mcp get laya
~~~

使用已验证的 mps 或 cpu 和绝对解释器路径，不依赖终端激活状态。LAYA_MODELS 只是预加载集合，不是模型白名单。LAYA_PRELOAD=0 将加载推迟到首次调用。

重新加载 MCP 或重新打开 Codex，在新任务输入：

> 调用 laya_status，再用 laya_predict、model=multilingual 判断“商品不能开机，我要退款”属于售前、售后还是其他。调用后检查实际设备，报告结果和耗时。不要用 laya_route 代替推理，不自行改用云端服务。

工具加载超时时，在实际配置文件已有 [mcp_servers.laya] 表内、command 和 args 同级添加以下建议值，不放入 env 子表，不创建重复表：

~~~toml
startup_timeout_sec = 60
tool_timeout_sec = 180
~~~

先完成第 5 步模型下载，再处理超时。[Codex MCP 文档](https://developers.openai.com/codex/mcp)

## 7．可选：本机 HTTP 接口

仅其他软件需要 HTTP 时使用，与 MCP 同时运行可能重复加载模型。原终端执行：

~~~bash
export LAYA_HOST=127.0.0.1
export LAYA_PORT=8000
export LAYA_PRELOAD=1
export LAYA_MODELS=multilingual
"$layaPython" -m laya.serve
~~~

另开终端：

~~~bash
curl --fail-with-body http://127.0.0.1:8000/health
curl --fail-with-body http://127.0.0.1:8000/v1/systemone \
  -H 'Content-Type: application/json' \
  -d '{"model":"multilingual","state":{"text":"商品坏了，我要退款。"},"questions":{"refund":{"type":"noul","instructions":"客户明确要求退款。"}}}'
~~~

旧 curl 不支持 --fail-with-body 时改用 -f。健康响应不证明推理成功；health 的 device 可能只是配置偏好。/v1/systemone 不是 MCP URL。Ctrl+C 停服务。[HTTP 实现](https://github.com/NandhaKishorM/laya/blob/main/laya/serve.py)

## 8．离线与隐私边界

完成下载后，在同一环境设置并重跑：

~~~bash
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
"$layaPython" "$layaRoot/smoke_test.py"
~~~

这检查当前 checkpoint 的缓存推理，不证明整个系统绝无网络活动。MCP 若要同样限制，将两个变量加入持久 env；请求未缓存模型仍可能失败。

本地 Laya 无需向 Jev 上传状态，但 Codex 主模型仍按其服务方式处理消息。不能把此方案描述成“Codex 全离线”。

## 9．故障排查与维护

| 现象 | 下一步 |
|---|---|
| M 系列 Python 显示 x86_64 | 换原生 arm64 终端和 Python，新建环境，不混架构。 |
| MPS 不可用 | 查系统和 PyTorch；明确改 CPU 时同步改 MCP 配置。 |
| unsupported autocast / 算子错误 | 留存报错，在新环境核对受支持版本组合，或明确改 CPU。 |
| Intel 无 torch wheel | 本路线阻塞，不保证降级可行；另评估运行时。 |
| 下载或 TLS 失败 | 查网络、时间和证书，不关闭证书验证或悄悄更换来源。 |
| 内存压力大 | 停重复实例，缩短输入，不预加载全部模型。 |
| 有工具名但无结果 | 查模型加载和工具超时；laya_route 不执行判断模型前向推理。 |
| 中文不可靠 | 用 multilingual、清晰少量选项和独立样本；置信度不是正确保证。 |

停用：

~~~bash
codex mcp remove laya
~~~

重新加载 MCP；若进程仍驻留，正常退出启动它的 Codex 会话。移除注册不会删除模型；也可在已有服务表设置 enabled=false。

升级前保留版本清单，在新目录测试后切换。删除前人工确认完整路径和内容，本教程不提供递归删除命令，不设置开机启动，不开放局域网端口。

## 10．验收与来源

分层确认：依赖可导入 → 真实推理及设备正确 → Codex 工具调用成功 → 业务样本达标。前三层不自动证明第四层。

- [Laya 作者仓库](https://github.com/NandhaKishorM/laya)
- [PyPI](https://pypi.org/project/laya/)
- [多语言模型卡](https://huggingface.co/convaiinnovations/laya-multilingual)
- [Apple PyTorch/MPS 要求](https://developer.apple.com/metal/pytorch/)
- [MCP 源码](https://github.com/NandhaKishorM/laya/blob/main/laya/mcp/server.py)
- [Codex MCP](https://developers.openai.com/codex/mcp)

运行时验证尚未完成：请在目标 Mac 按本文验收步骤实测。
