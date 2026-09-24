# Laya 本地部署教程｜Windows 版

目标：在 Windows 电脑本地运行 Laya，并让 Codex 按需调用分类和判断工具。

版本：v1｜资料核对：2026-09-24\
验证范围：官方资料核对、教程代码静态检查；本次未安装 Laya、未下载权重、未完成 Windows 推理实测。

## 先选路线

| 电脑条件 | 本文路线 |
|---|---|
| Windows 10/11、NVIDIA 显卡与可用驱动 | CUDA |
| 无 NVIDIA 显卡，或主动选择 CPU | CPU |
| 其他显卡加速方案 | 不在本教程验证范围内，先选择 CPU |

建议为依赖和缓存留出 10GB 以上磁盘、优先 16GB 以上内存；这是余量建议，不是官方最低配置。

安装阶段需要访问 PyPI、PyTorch 下载站和 Hugging Face。本地 Laya 推理不需要 Jev Key。默认先使用中文多语言模型，完成小样本检查后再接 Codex。

完成标志：真实模型推理通过、实际设备正确、Codex 真正调用 laya_predict。导入成功或工具列表出现名称都不能替代这些检查。

## 1．准备 Python 和独立目录

打开普通 PowerShell，每个步骤成功后再继续。无需激活虚拟环境或修改执行策略。

~~~powershell
python --version
py --list
Get-Command python, py -ErrorAction SilentlyContinue
~~~

没有可用的 64 位 Python 时，从 [Python 官方 Windows 下载页](https://www.python.org/downloads/windows/)安装。建议 Python 3.11 或 3.12；Laya 要求至少 3.10，依赖也必须兼容。[包信息](https://pypi.org/project/laya/)

下面以 Python 3.11 为例；若装的是 3.12，将第一行版本改为 3.12。

~~~powershell
$basePython = (& py -3.11 -c "import sys; print(sys.executable)").Trim()
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $basePython)) {
    throw '先解决 Python 解释器问题。'
}
& $basePython -c "import sys, struct; print(sys.executable); print(sys.version); assert sys.version_info >= (3,10); assert struct.calcsize('P') == 8"
if ($LASTEXITCODE -ne 0) { throw '需要 Python 3.10+、64 位解释器。' }
~~~

如果 py 启动器不可用，但 python 可运行，改用下面命令取得真实路径，再做版本检查：

~~~powershell
$basePython = (& python -c "import sys; print(sys.executable)").Trim()
& $basePython -c "import sys, struct; print(sys.executable); print(sys.version); assert sys.version_info >= (3,10); assert struct.calcsize('P') == 8"
~~~

不要把 WindowsApps 中不能执行的别名当作真实解释器。两种命令都失败时，修复官方 Python 安装。

以下创建新部署目录：有 E 盘时使用 E:\Codex\Laya；没有 E 盘时从当前用户目录生成完整路径。这是待创建的目标，不表示已经存在。

~~~powershell
$ErrorActionPreference = 'Stop'
$layaRoot = if (Test-Path -LiteralPath 'E:\') {
    'E:\Codex\Laya'
} else {
    Join-Path $env:USERPROFILE 'Laya'
}
if (Test-Path -LiteralPath $layaRoot) {
    throw "目录已存在：$layaRoot。先检查旧部署，或改用新的版本目录。"
}
New-Item -ItemType Directory -Path $layaRoot | Out-Null
& $basePython -m venv (Join-Path $layaRoot '.venv')
if ($LASTEXITCODE -ne 0) { throw '创建虚拟环境失败。' }
$layaPython = Join-Path $layaRoot '.venv\Scripts\python.exe'
& $layaPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'pip 更新失败。' }
Write-Host "部署目录：$layaRoot"
Write-Host "专用 Python：$layaPython"
~~~

后续在同一个 PowerShell 窗口执行。新开窗口时，重新设置 layaRoot、layaPython 和环境变量。

## 2．安装 PyTorch：只选一条路线

### A．NVIDIA CUDA

先运行 nvidia-smi，确认显卡和驱动可识别：

~~~powershell
nvidia-smi
~~~

打开 [PyTorch 安装选择器](https://pytorch.org/get-started/locally/)，选 Windows / Pip / Python / 与驱动兼容的 CUDA 构建。下面给出 CUDA 12.8 源的示例；若选择器要求其他构建，按官方结果调整下载源。

~~~powershell
& $layaPython -m pip install torch --index-url https://download.pytorch.org/whl/cu128
if ($LASTEXITCODE -ne 0) { throw 'CUDA PyTorch 安装失败。' }
$env:LAYA_DEVICE = 'cuda'
& $layaPython -c "import torch; print(torch.__version__, torch.version.cuda); assert torch.cuda.is_available(), 'CUDA unavailable'; print(torch.cuda.get_device_name(0)); print(torch.ones(1, device='cuda'))"
if ($LASTEXITCODE -ne 0) { throw 'GPU 张量运算失败，不继续。' }
~~~

使用预编译 PyTorch 包通常不需要单独安装完整 CUDA Toolkit。也不默认安装 nightly。

### B．CPU

~~~powershell
& $layaPython -m pip install torch --index-url https://download.pytorch.org/whl/cpu
if ($LASTEXITCODE -ne 0) { throw 'CPU PyTorch 安装失败。' }
$env:LAYA_DEVICE = 'cpu'
& $layaPython -c "import torch; print(torch.__version__); print(torch.ones(1))"
if ($LASTEXITCODE -ne 0) { throw 'CPU 运算失败。' }
~~~

CPU 路线用于本地功能验证，不承诺达到作者的 GPU 延迟。

## 3．安装 Laya 和扩展

~~~powershell
& $layaPython -m pip install 'laya[mcp,serve]'
if ($LASTEXITCODE -ne 0) { throw 'Laya 安装失败。' }
& $layaPython -m pip check
if ($LASTEXITCODE -ne 0) { throw '先修复依赖冲突。' }
& $layaPython -I -c "from importlib.metadata import version; import laya; import laya.mcp.server; print('laya', version('laya'))"
if ($LASTEXITCODE -ne 0) { throw 'Laya/MCP 导入失败。' }

$env:LAYA_ROOT = $layaRoot
$env:HF_HOME = Join-Path $layaRoot 'model-cache'
$env:USE_TF = '0'
$env:PYTHONUTF8 = '1'
$env:HF_HUB_DISABLE_SYMLINKS = '1'
$env:HF_HUB_DISABLE_SYMLINKS_WARNING = '1'
$lockFile = Join-Path $layaRoot ("requirements-" + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.txt')
& $layaPython -m pip freeze | Set-Content -LiteralPath $lockFile -Encoding UTF8
~~~

安装扩展不代表服务已运行。主线只启用 MCP，HTTP 是后文可选项。[依赖声明](https://github.com/NandhaKishorM/laya/blob/main/pyproject.toml)

核对时作者主分支标为 0.3.17；PyPI 发布版、主分支和权重是不同对象。以实际输出及版本清单为准，不把未安装的版本写成已验证组合。

## 4．下载模型并做真实推理

以下整块代码会创建测试文件，再执行。只请求多语言 checkpoint；首次运行需要下载。结果中的耗时不含模型初始化，不是 Codex 端到端延迟。

~~~powershell
@'
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
'@ | Set-Content -LiteralPath (Join-Path $layaRoot 'smoke_test.py') -Encoding UTF8
& $layaPython (Join-Path $layaRoot 'smoke_test.py')
if ($LASTEXITCODE -ne 0) { throw '真实推理失败，不继续注册 MCP。' }
~~~

成功信号：

- requested_device 与 actual_device 一致；请求 GPU 却退回 CPU 时，本测试报错。
- 返回三个场景、合法分类及概率，并保存带时间编号的 JSON 报告。
- 检查 sample_matches；若不是 3，先检查基础误判，再考虑业务使用。
- 三个样例全对也不是准确率评测，只是小样本检查。

Laya 存在设备回退逻辑，因此要读实际模型设备，不能只看 CUDA=True。[设备实现](https://github.com/NandhaKishorM/laya/blob/main/laya/agent.py)

## 5．接入 Codex 本地 MCP

~~~powershell
codex --version
codex mcp list
~~~

找不到 codex 时，按 [Codex CLI 官方说明](https://developers.openai.com/codex/cli/)安装或配置命令行入口。不要复制其他电脑的带版本号安装路径。

下面会新增持久 MCP 配置。列表已有 laya 时，先查看和保留旧配置，不重复添加。可备份实际配置：

~~~powershell
$layaCodexDir = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
$layaCodexConfig = Join-Path $layaCodexDir 'config.toml'
if (Test-Path -LiteralPath $layaCodexConfig) {
    Copy-Item -LiteralPath $layaCodexConfig -Destination ($layaCodexConfig + '.before-laya-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.bak')
}
Write-Host "配置位置：$layaCodexConfig"
~~~

确认没有同名注册后执行：

~~~powershell
$layaMcpArgs = @(
    'mcp', 'add', 'laya',
    '--env', "LAYA_DEVICE=$env:LAYA_DEVICE",
    '--env', 'LAYA_PRELOAD=0',
    '--env', 'LAYA_MODELS=multilingual',
    '--env', "HF_HOME=$env:HF_HOME",
    '--env', 'USE_TF=0',
    '--env', 'PYTHONUTF8=1',
    '--', $layaPython, '-m', 'laya.mcp.server'
)
codex @layaMcpArgs
if ($LASTEXITCODE -ne 0) { throw 'MCP 注册失败。' }
codex mcp get laya
~~~

STDIO 不需要开放端口。LAYA_PRELOAD=0 表示首次调用加载模型；LAYA_MODELS 只是预加载集合，不是模型白名单。中文调用应明确 model="multilingual"。

重新加载 MCP 或重新打开 Codex，在新任务中输入：

> 调用 laya_status 查看环境，再调用 laya_predict，以 multilingual 模型将“商品无法开机，我要退货退款”分到售前、售后或其他。调用后检查实际设备，展示真实结果。不要用 laya_route 代替推理，不自行改用云端服务。

工具超时时，在实际配置文件已有的 [mcp_servers.laya] 表内、command 和 args 同级添加以下建议值；不要放入 env 子表或创建重复表：

~~~toml
startup_timeout_sec = 60
tool_timeout_sec = 180
~~~

先在第 4 步完成权重下载，不用无限延长超时掩盖错误。[Codex MCP 文档](https://developers.openai.com/codex/mcp)

## 6．可选：提供本机 HTTP API

仅其他应用需要 HTTP 时使用。与 MCP 同时运行可能重复占用显存。在原 PowerShell 窗口：

~~~powershell
$env:LAYA_HOST = '127.0.0.1'
$env:LAYA_PORT = '8000'
$env:LAYA_PRELOAD = '1'
$env:LAYA_MODELS = 'multilingual'
& $layaPython -m laya.serve
~~~

保持该窗口运行，另开 PowerShell：

~~~powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health'
$layaRequest = @{
    model = 'multilingual'
    state = @{ text = '商品坏了，我要退款。' }
    questions = @{ refund = @{ type = 'noul'; instructions = '客户明确要求退款。' } }
} | ConvertTo-Json -Depth 8
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/v1/systemone' -Method Post -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($layaRequest))
~~~

/health 的 device 可能只是配置偏好；健康响应不是实际设备证据。/v1/systemone 是 HTTP 推理接口，不能当作 MCP URL。按 Ctrl+C 停服务。[HTTP 源码](https://github.com/NandhaKishorM/laya/blob/main/laya/serve.py)

## 7．故障排查

| 现象 | 下一步 |
|---|---|
| py 无法执行、跳商店 | 用第 1 步可运行的 python 确认路径；否则修复 Python 安装。 |
| TLS、证书、连接错误 | 检查系统时间、网络和已授权代理，保留完整报错；不要关闭证书验证。 |
| CUDA=False | 核对驱动和 PyTorch 构建；能在 CPU 跑不等于 GPU 成功。 |
| Hugging Face 下载失败 | 恢复官方访问后重试，不静默切换镜像、云端 API 或来源不明权重。 |
| 缺少 rl_agent_config.json | 检查下载完整性和所选模型，不能手工伪造配置。 |
| 变慢或显存不足 | 查 actual_device、重复进程和输入长度；明确改 CPU 时同步改 MCP 配置。 |
| MCP 有名字但不能推理 | 查导入错误、权重缓存和超时；status/route 不是模型推理。 |
| 中文效果差 | 强制 multilingual，缩短 state、减少选项，用自己的中文样本检验。 |

## 8．停用、更新与验收

停用接入但保留安装文件：

~~~powershell
codex mcp remove laya
~~~

重新加载 MCP；如进程仍驻留，正常退出启动它的 Codex 会话。也可在已有 laya 配置表设置 enabled=false。

升级前保存版本清单，在新目录建立新环境，验证后再切换。删除前人工确认完整目录及内容，本教程不提供批量删除命令。

分开记录四层结果：依赖可导入、真实推理成功、Codex 调用成功、业务样本达标。前三层通过不自动证明第四层。本地 Laya 也不等于整个 Codex 会话离线。

## 官方来源

- [Laya 作者仓库](https://github.com/NandhaKishorM/laya)
- [PyPI 包](https://pypi.org/project/laya/)
- [多语言模型卡](https://huggingface.co/convaiinnovations/laya-multilingual)
- [Laya MCP 实现](https://github.com/NandhaKishorM/laya/blob/main/laya/mcp/server.py)
- [PyTorch 安装](https://pytorch.org/get-started/locally/)
- [Codex MCP](https://developers.openai.com/codex/mcp)

运行时验证尚未完成：请在目标 Windows 电脑按本文验收步骤实测。
