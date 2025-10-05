

import asyncio
import re
from typing import Annotated

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient


# ==================== 工具1: Claude 生成代码 ====================

async def run_claude_generate(
    task: Annotated[str, "生成任务描述"]
) -> str:
    """Claude Code 生成代码（使用当前目录）"""
    try:
        # 使用当前目录，避免路径参数问题
        import os
        cwd = os.getcwd()

        # 确保是 Git 仓库
        git_check = await asyncio.create_subprocess_exec(
            "git", "rev-parse", "--git-dir",
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await git_check.communicate()

        if git_check.returncode != 0:
            init_proc = await asyncio.create_subprocess_exec(
                "git", "init",
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await init_proc.communicate()

        # 验证 Claude CLI 是否可用
        check = await asyncio.create_subprocess_exec(
            "which", "claude",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await check.communicate()

        if check.returncode != 0:
            return "⚠️ Claude CLI 未找到\n\n检查: which claude\n安装: 请参考 Claude CLI 官方指南"

        # Claude 生成代码
        process = await asyncio.create_subprocess_exec(
            "claude",
            "-p", task,
            "--permission-mode", "acceptEdits",
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            return f"✅ Claude 生成完成\n\n{stdout.decode()}"
        else:
            return f"❌ 生成失败: {stderr.decode()}"

    except Exception as e:
        return f"❌ 异常: {str(e)}"


# ==================== 工具2: Codex 审查（正确方式）====================

async def run_codex_review(
    review_task: Annotated[str, "审查任务描述"]
) -> str:
    """
    Codex CLI 审查代码（使用当前目录）

    Codex 会自动检测 git diff、读取文件、运行测试
    """
    try:
        import os
        cwd = os.getcwd()

        # 验证 Codex 是否可用
        check = await asyncio.create_subprocess_exec(
            "which", "codex",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await check.communicate()

        if check.returncode != 0:
            return "⚠️ Codex CLI 未找到\n\n检查: which codex\n安装: npm install -g @openai/codex"

        # 调用 Codex
        process = await asyncio.create_subprocess_exec(
            "codex",
            "exec",
            review_task,
            "--full-auto",
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            review_result = stdout.decode()

            # 检查是否通过
            if re.search(r"\b(lgtm|looks good|approved|approve|no issues)\b", review_result, re.IGNORECASE):
                return f"✅ REVIEWER_APPROVED - Codex 审查通过\n\n{review_result}"
            else:
                return f"📋 Codex 审查报告\n\n{review_result}"
        else:
            error = stderr.decode()
            if "git" in error.lower():
                return f"⚠️ Codex 需要 Git 仓库\n\n运行: git init\n\n错误: {error}"
            return f"⚠️ Codex 审查失败: {error}"

    except Exception as e:
        return f"⚠️ 审查异常: {str(e)}"


# ==================== 工具3: Claude 修复 ====================

async def run_claude_fix(
    fix_task: Annotated[str, "修复任务描述"]
) -> str:
    """Claude 修复代码（使用当前目录）"""
    try:
        import os
        cwd = os.getcwd()

        check = await asyncio.create_subprocess_exec(
            "which", "claude",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await check.communicate()

        if check.returncode != 0:
            return "⚠️ Claude CLI 未找到\n\n检查: which claude\n安装: 请参考 Claude CLI 官方指南"

        process = await asyncio.create_subprocess_exec(
            "claude",
            "-p", fix_task,
            "--permission-mode", "acceptEdits",
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            return f"修复完成\n\n{stdout.decode()}"
        else:
            return f"修复失败: {stderr.decode()}"

    except Exception as e:
        return f"修复异常: {str(e)}"


# ==================== 创建工作流 ====================

async def create_cross_review_workflow():
    """创建正确的交叉审查工作流"""

    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

    # 1. Generator（Claude）
    generator = AssistantAgent(
        name="Generator",
        model_client=model_client,
        tools=[run_claude_generate],
        system_message="""你是代码生成器，使用 Claude Code。

任务：
1. 调用 run_claude_generate 生成代码
2. 报告生成的文件路径

限制：不要在回复中输出 REVIEWER_APPROVED 关键字。

只在首次调用工具。"""
    )

    # 2. Reviewer（Codex）
    reviewer = AssistantAgent(
        name="Reviewer",
        model_client=model_client,
        tools=[run_codex_review],
        system_message="""你是代码审查员，使用 Codex CLI。

任务：
1. 构造详细的审查任务描述，包括：
   - 要检查的方面（安全、性能、质量）
   - 需要的输出格式
2. 调用 run_codex_review
3. 分析结果：
   - 如果看到 "REVIEWER_APPROVED"，输出 "REVIEWER_APPROVED - 审查通过"
   - 如果有问题，输出 "发现问题: [总结]"

重要：Codex 会自动检测 git diff 和运行测试，无需额外操作。"""
    )

    # 3. Fixer（Claude）
    fixer = AssistantAgent(
        name="Fixer",
        model_client=model_client,
        tools=[run_claude_fix],
        system_message="""你是代码修复员，使用 Claude Code。

任务：
1. 接收审查报告
2. 构造详细的修复任务描述
3. 调用 run_claude_fix
4. 报告修复结果

限制：不要在回复中输出 REVIEWER_APPROVED 关键字。

不要自己判断是否通过，让审查员决定。"""
    )

    # 终止条件
    termination = TextMentionTermination("REVIEWER_APPROVED") | MaxMessageTermination(20)

    # RoundRobin 支持循环
    team = RoundRobinGroupChat(
        participants=[generator, reviewer, fixer],
        termination_condition=termination,
    )

    return team


# ==================== 主函数 ====================

async def main():
    team = await create_cross_review_workflow()

    requirement = """
实现 Python 快速排序算法：
1. 支持自定义比较函数
2. 包含输入验证
3. 完整的文档字符串
4. 处理边界情况（空列表、单元素）
"""

    print("🚀 正确的交叉审查工作流")
    print("📋 基于真实的 Codex CLI API")
    print("=" * 80)

    await Console(team.run_stream(task=requirement))

    print("\n" + "=" * 80)
    print("✅ 工作流完成")


if __name__ == "__main__":
    asyncio.run(main())
