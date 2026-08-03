# QM 从零安装到邮箱多用户登录完整指南

> 适用项目：[`yc-software/qm`](https://github.com/yc-software/qm)  
> 适用场景：macOS 本机测试、Pi Harness、Docker Postgres、QM 内置 Auth、Resend 邮件一次性链接、多人邮箱白名单、Admin Dashboard  
> 文档性质：基于一次真实本机安装过程整理。文中的密钥、邮箱、域名和模型名称全部使用占位符，不能原样用于生产。

---

## 0. 先理解我们最终要搭建什么

本指南最终会启动 6 个组成部分：

| 组件 | 本机端口 | 作用 |
|---|---:|---|
| PostgreSQL | `5432` | 持久化会话、运行记录、Memory、权限、一次性登录链接防重放等 |
| QM Core | `8080` | 身份、权限、Agent 调度、Pi Harness、Memory、Keychain 等核心能力 |
| Web UI | `8096` | 普通用户使用的聊天、文件、Memory、Skills、Keychain 等界面 |
| Admin Dashboard | `8090` | 管理用户、Scope、权限、审计、错误、指标、配置等 |
| QM Auth | `8099` | QM 内置 OIDC 身份提供商，通过邮件发送一次性登录链接 |
| Portal | `8097` | 唯一对浏览器开放的入口，负责登录、Session 和反向代理 Web UI/Admin |

浏览器正常只访问：

```text
http://127.0.0.1:8097
```

请求链路如下：

```text
浏览器
  ↓
Portal :8097
  ├─ /                 → Web UI :8096
  ├─ /admin/           → Admin Dashboard :8090
  └─ /idp/*            → Auth :8099
                           ↓
                       Resend API
                           ↓
                      用户邮箱收件箱

所有业务与权限请求最终都会进入 Core :8080
Core 使用 PostgreSQL :5432 保存持久化状态
```

### “非 Dev 模式”在本指南里的准确含义

本机测试配置中：

- Web UI 的不安全 Principal 输入框已经关闭。
- `ALLOW_UNSIGNED_TEST_IDENTITY=0`。
- 浏览器身份必须由 Portal 签名后才能进入 Web UI。
- `PORTAL_LOCAL_AUTH_BYPASS` 不启用。
- 用户必须通过真实邮箱一次性链接证明身份。

但是本机仍然使用 `http://127.0.0.1`，不是 HTTPS。为了允许本机 HTTP，Portal 和 Auth 启动时使用 `NODE_ENV=test`。所以它属于：

> 真实邮箱身份 + Portal 权限链路的本机测试环境，而不是可以直接暴露到互联网的生产环境。

生产环境必须改用 HTTPS，并让 Portal/Auth 运行 `NODE_ENV=production`。

---

## 1. 安装前的环境要求

### 1.1 操作系统

本文以 macOS 为例。Linux 也可以使用同样架构，但安装 Node、Docker 和打开浏览器的命令不同。

### 1.2 Node.js 与 npm

当前 QM 根目录的 `package.json` 要求：

```text
Node.js >= 24.15.0
npm     >= 11.10.0
```

不要只满足各插件中较宽松的 `Node >= 24`；应以根项目要求为准。

检查版本：

```bash
node --version
npm --version
```

示例合格输出：

```text
v24.18.0
11.10.0 或更高
```

如果使用 `nvm`：

```bash
nvm install 24.18.0
nvm use 24.18.0
npm install --global npm@11.10.0
```

再次验证：

```bash
node --version
npm --version
```

如果机器里同时安装了多个 Node，必须确认当前 Terminal 使用的 `node` 和 `npm` 属于同一套 Node 环境：

```bash
which node
which npm
node -p 'process.execPath'
```

### 1.3 Git

检查：

```bash
git --version
```

macOS 如果提示安装 Command Line Tools，按系统提示完成即可。

### 1.4 Docker Desktop

本指南使用 Docker 同时承担：

- PostgreSQL 数据库；
- QM 本地 Agent Sandbox。

检查客户端：

```bash
docker --version
```

检查 Docker 引擎是否真正启动：

```bash
docker info
```

只有 `docker --version` 成功并不代表 Docker Desktop 已经启动；`docker info` 也必须成功。

### 1.5 Resend 账号

QM 内置 Auth 原生支持两种发信方式：

```text
smtp
resend
```

本指南选择 Resend，因此需要：

1. 一个 Resend 账号；
2. 一个具有发送权限的 API Key；
3. 单邮箱测试时，可使用 Resend 测试发件地址；
4. 真正给多个外部用户发邮件时，需要在 Resend 验证自己控制的域名或子域名。

创建 API Key 后，只会显示一次完整值。不要提交进 Git。

---

## 2. 下载 QM 源代码

选择工作目录：

```bash
cd ~/Desktop
```

克隆官方仓库：

```bash
git clone https://github.com/yc-software/qm.git
cd qm
```

确认远程地址：

```bash
git remote -v
```

应指向：

```text
https://github.com/yc-software/qm.git
```

查看当前分支与工作区状态：

```bash
git status
```

---

## 3. 安装依赖并构建 Web UI

QM 根项目以及各插件都有自己的 `package-lock.json`。为了得到可复现安装，干净克隆优先使用 `npm ci`。

### 3.1 安装 Core 依赖

在 QM 根目录执行：

```bash
npm ci
```

### 3.2 安装并构建 Web UI

```bash
cd plugins/web-ui
npm ci
npm run build
cd ../..
```

构建完成后，Web UI Server 会使用生成的静态文件。若没有构建，启动日志会提示 `dist-web/ not built`。

### 3.3 安装 Portal、Auth、Admin 依赖

```bash
cd plugins/portal
npm ci
cd ../..

cd plugins/auth
npm ci
cd ../..

cd plugins/admin
npm ci
cd ../..
```

Admin 本身几乎没有运行时依赖，但仍建议按锁文件执行安装，以保持所有插件环境一致。

### 3.4 基础校验

```bash
npm run typecheck
```

如果只是进行本机使用，不一定要运行完整测试套件；如果要修改源码，至少再执行相关测试。

---

## 4. 构建本地 Agent Sandbox

当 `SANDBOX_BACKEND=local` 时，Agent 的命令、文件和工具会运行在 Docker Sandbox 中。

在 QM 根目录执行：

```bash
npm run sandbox:local:build
```

默认生成镜像：

```text
qm-sandbox-local:latest
```

验证：

```bash
docker image inspect qm-sandbox-local:latest
```

Apple Silicon Mac 上，QM 当前构建脚本使用 `linux/amd64`，Docker Desktop 会使用架构模拟，第一次构建可能比较慢。

---

## 5. 启动 PostgreSQL

### 5.1 本机测试用 Docker Postgres

下面的命令只把数据库端口绑定到 `127.0.0.1`，并创建独立数据卷：

```bash
docker run -d \
  --name qm-auth-postgres \
  --restart unless-stopped \
  -e POSTGRES_DB=qm \
  -e POSTGRES_HOST_AUTH_METHOD=trust \
  -p 127.0.0.1:5432:5432 \
  -v qm-auth-postgres-data:/var/lib/postgresql/data \
  postgres:16-alpine
```

说明：

- 容器名：`qm-auth-postgres`；
- 数据库名：`qm`；
- 数据卷：`qm-auth-postgres-data`；
- `trust` 只适合绑定到本机回环地址的测试环境；
- 生产环境必须使用强密码、受控网络和 TLS。

### 5.2 检查数据库状态

```bash
docker ps --filter name=qm-auth-postgres
docker exec qm-auth-postgres pg_isready -U postgres -d qm
```

期望看到：

```text
/var/run/postgresql:5432 - accepting connections
```

如果容器已经存在但停止了：

```bash
docker start qm-auth-postgres
```

---

## 6. 生成所有安全密钥

至少生成以下互不相同的密钥：

| 变量 | 用途 |
|---|---|
| `CORE_SIGNING_SECRET` | Core 与内部 Surface 的签名认证 |
| `CAPABILITY_SECRET` | 每次 Agent Turn 的 Capability Token |
| `PORTAL_IDENTITY_SECRET` | Portal 向 Web UI/Admin/Core 传递签名身份 |
| `CONNECTOR_SECRET_KEY` | Keychain、Connector、模型凭据等加密 |
| `PORTAL_SESSION_SECRET` | Portal 浏览器 Session |
| `AUTH_CLIENT_SECRET` | Portal 作为 OIDC Client 向 Auth 换 Token |
| `AUTH_TOKEN_SECRET` | Auth 封装邮件链接、授权码、Access Token |
| `AUTH_SIGNING_JWK` | Auth 签署 OIDC ID Token 的 P-256 私钥 |

### 6.1 生成普通随机密钥

每个变量都单独运行一次，不能复用输出：

```bash
openssl rand -hex 32
```

建议在密码管理器中临时记录，并明确标注变量名称。

### 6.2 生成 P-256 私有 JWK

需要先完成 `npm ci`，然后在 QM 根目录执行：

```bash
node --input-type=module -e "import { generateKeyPair, exportJWK } from 'jose'; const { privateKey } = await generateKeyPair('ES256', { extractable: true }); console.log(JSON.stringify(await exportJWK(privateKey)))"
```

输出是一行 JSON，例如：

```json
{"kty":"EC","x":"...","y":"...","crv":"P-256","d":"..."}
```

整行保存为 `AUTH_SIGNING_JWK`。其中 `d` 是私钥，不能提交到 Git。

---

## 7. 创建 QM 根目录 `.env`

在 QM 根目录创建：

```text
.env
```

QM 的 `.gitignore` 已忽略 `*.env`，但仍要检查：

```bash
git check-ignore -v .env
```

期望得到一条 ignore 规则。下面是完整模板。

```dotenv
# --------------------------------------------------
# Core / Harness
# --------------------------------------------------
HARNESS=pi
HARNESS_SECURITY_POSTURE=auto
ORG_ID=local
PORT=8080

# 根据实际可用的 Pi 模型填写
PI_MODEL=<PI_MODEL_ID>

# 本地 Docker Sandbox
SANDBOX_BACKEND=local
LOCAL_SANDBOX_IMAGE=qm-sandbox-local:latest

# --------------------------------------------------
# Core secrets：每项必须不同
# --------------------------------------------------
CORE_SIGNING_SECRET=<64_HEX_CORE_SECRET>
CAPABILITY_SECRET=<64_HEX_CAPABILITY_SECRET>
PORTAL_IDENTITY_SECRET=<64_HEX_PORTAL_IDENTITY_SECRET>
CONNECTOR_SECRET_KEY=<64_HEX_CONNECTOR_SECRET>

# 要求 Surface 使用 Portal 签名身份
REQUIRE_SIGNED_PORTAL_IDENTITY=1

# --------------------------------------------------
# PostgreSQL durability
# --------------------------------------------------
DATABASE_URL=postgresql://postgres@127.0.0.1:5432/qm
SESSION_STORE=postgres
RUN_STORE=postgres

# --------------------------------------------------
# Initial administrator seed
# 只在 admin_grants 表为空时作为一次性种子
# 邮箱必须使用小写
# --------------------------------------------------
ADMIN_GRANTS=<ADMIN_EMAIL>:org_admin

# 浏览器唯一入口
PUBLIC_WEB_URL=http://127.0.0.1:8097

# --------------------------------------------------
# QM built-in Auth
# --------------------------------------------------
AUTH_ISSUER=http://127.0.0.1:8097/idp
AUTH_CLIENT_ID=qm-portal
AUTH_CLIENT_SECRET=<64_HEX_AUTH_CLIENT_SECRET>
AUTH_REDIRECT_URI=http://127.0.0.1:8097/auth/callback
AUTH_SIGNING_JWK=<ONE_LINE_P256_PRIVATE_JWK_JSON>
AUTH_TOKEN_SECRET=<64_HEX_AUTH_TOKEN_SECRET>

# 单邮箱或多邮箱白名单，逗号分隔
AUTH_ALLOWED_EMAILS=<ADMIN_EMAIL>,<USER_2_EMAIL>,<USER_3_EMAIL>

# 单邮箱测试可临时使用 Resend 测试发件地址
# 多用户正式收信必须换成已验证域名下的发件人
AUTH_EMAIL_FROM="QM <onboarding@resend.dev>"
AUTH_BRAND_NAME="QM Local"
AUTH_EMAIL_TRANSPORT=resend
RESEND_API_KEY=<RESEND_API_KEY>

# --------------------------------------------------
# Portal Session / upstreams
# --------------------------------------------------
PORTAL_SESSION_SECRET=<64_HEX_PORTAL_SESSION_SECRET>
AUTH_BROKER_UPSTREAM=http://127.0.0.1:8099
AUTH_BROKER_PREFIX=/idp
ADMIN_UPSTREAM=http://127.0.0.1:8090

# --------------------------------------------------
# Portal → built-in Auth OIDC wiring
# --------------------------------------------------
OIDC_AUTH_ENDPOINT=http://127.0.0.1:8097/idp/authorize
OIDC_TOKEN_ENDPOINT=http://127.0.0.1:8099/token
OIDC_USERINFO_ENDPOINT=http://127.0.0.1:8099/userinfo
OIDC_ISSUER=http://127.0.0.1:8097/idp
OIDC_JWKS_URI=http://127.0.0.1:8099/.well-known/jwks.json
OIDC_SCOPES="openid email"
OIDC_PRINCIPAL_CLAIM=email
OIDC_ALLOWED_EMAILS=<ADMIN_EMAIL>,<USER_2_EMAIL>,<USER_3_EMAIL>
OIDC_CLIENT_ID=qm-portal
OIDC_CLIENT_SECRET=<与_AUTH_CLIENT_SECRET_完全相同>

# 可选：本机测试预算
BUDGET_USD_PER_WINDOW=1
ORG_BUDGET_USD_PER_WINDOW=2
```

### 7.1 不能出现的配置

邮箱登录模式下不要启用：

```dotenv
PORTAL_LOCAL_AUTH_BYPASS=1
ALLOW_UNSIGNED_TEST_IDENTITY=1
```

前者会让 Portal 绕过 OIDC，后者会让 Web UI 接受不安全身份。

### 7.2 Auth 与 Portal 白名单必须一致

手工配置时必须同时维护：

```dotenv
AUTH_ALLOWED_EMAILS=...
OIDC_ALLOWED_EMAILS=...
```

- Auth 使用第一份列表决定是否发送/接受登录；
- Portal 使用第二份列表再次约束 OIDC 身份；
- 两边不一致会造成“邮件发出但 Portal 拒绝”或其他难以判断的问题。

---

## 8. 配置 Web UI 为 Portal 身份模式

创建：

```text
plugins/web-ui/.env
```

内容：

```dotenv
CORE_API_URL=http://127.0.0.1:8080
CORE_ORG_ID=local
PORT=8096
WEB_UI_PUBLIC_URL=http://127.0.0.1:8097
WEB_UI_PRINCIPALS=
ALLOW_UNSIGNED_TEST_IDENTITY=0
CORE_SIGNING_SECRET=<与根目录_CORE_SIGNING_SECRET_相同>
NODE_ENV=production
```

本指南启动 Web UI 时会同时加载根 `.env` 和插件 `.env`：

```bash
node --env-file=../../.env --env-file=.env server/index.ts
```

因此 Web UI 会从根 `.env` 继承 `PORTAL_IDENTITY_SECRET`。如果不使用上述启动命令，而只加载插件 `.env`，则必须把相同的 `PORTAL_IDENTITY_SECRET` 加进插件 `.env`。

验证 `.env` 不会提交：

```bash
git check-ignore -v plugins/web-ui/.env
```

---

## 9. 配置 Pi Harness 与模型

身份登录与模型调用是两条独立链路：

- 即使没有模型密钥，邮件登录页面仍然可以工作；
- 只有实际发送聊天消息时才需要可用模型。

最小配置：

```dotenv
HARNESS=pi
PI_MODEL=<当前 Pi 能识别的模型 ID>
```

模型凭据可以通过 QM 支持的模型 Provider 配置或管理员界面录入。不要把生产模型密钥放进浏览器代码。

### 9.1 关于 Pi 使用 Codex OAuth

本次实测工作区使用了：

```dotenv
PI_CODEX_AUTH_PATH=./data/pi-auth/auth.json
```

但需要特别注意：当前工作区包含未提交的 Pi/Codex OAuth 兼容改动。干净克隆的上游版本是否支持该变量，应先检查：

```bash
rg PI_CODEX_AUTH_PATH src
```

如果没有结果，不要假定原版已经支持这条路径；应使用上游当前支持的模型认证方式，或者先移植并测试对应补丁。邮箱多用户登录本身不依赖 Pi/Codex OAuth。

---

## 10. 按正确顺序启动所有服务

建议开 5 个 Terminal 标签页。Postgres 由 Docker 后台运行。

启动顺序：

```text
Postgres → Core → Web UI → Auth → Admin → Portal
```

### 10.1 Terminal 1：启动 Core

在 QM 根目录：

```bash
node --env-file=.env src/index.ts
```

期望日志：

```text
[qm] listening on :8080 (org=local, store=postgres, runStore=postgres, ...)
```

必须看到：

```text
store=postgres
runStore=postgres
```

如果仍是 `memory`，说明 `DATABASE_URL`、`SESSION_STORE` 或 `RUN_STORE` 没有生效。

### 10.2 Terminal 2：启动 Web UI

```bash
cd plugins/web-ui
node --env-file=../../.env --env-file=.env server/index.ts
```

期望日志：

```text
[web-ui] surface on http://localhost:8096 → core http://127.0.0.1:8080 (org local)
```

### 10.3 Terminal 3：启动 Auth

从 QM 根目录运行：

```bash
NODE_ENV=test PORT=8099 \
node --env-file=.env plugins/auth/src/index.ts
```

期望日志：

```text
[auth] sign-in broker on http://localhost:8099 (..., resend email)
```

本机 HTTP 使用 `NODE_ENV=test`。生产部署必须换成 HTTPS 和 `NODE_ENV=production`。

### 10.4 Terminal 4：启动 Admin Dashboard

```bash
NODE_ENV=test \
PORT=8090 \
CORE_API_URL=http://127.0.0.1:8080 \
CORE_ORG_ID=local \
ADMIN_BASE_PATH=/admin \
node --env-file=.env plugins/admin/src/index.ts
```

期望日志：

```text
[admin-plugin] http://localhost:8090 → core http://127.0.0.1:8080 (org=local)
```

Admin `8090` 不应直接暴露给公网，只应由 Portal 访问。

### 10.5 Terminal 5：启动 Portal

```bash
NODE_ENV=test \
PORT=8097 \
PORTAL_PUBLIC_URL=http://127.0.0.1:8097 \
CORE_API_URL=http://127.0.0.1:8080 \
CORE_ORG_ID=local \
WEB_UI_UPSTREAM=http://127.0.0.1:8096 \
node --env-file=.env plugins/portal/src/index.ts
```

期望日志：

```text
[portal] public front door on http://localhost:8097 → web-ui/admin ...
```

本机测试出现以下警告是正常的：

```text
PORTAL_PUBLIC_URL is not https — cookies are NOT Secure (dev/test only)
```

它同时提醒：这套 HTTP 配置不能直接用于生产。

---

## 11. 启动后的健康检查

逐项执行：

```bash
curl -fsS http://127.0.0.1:8080/healthz
curl -fsS http://127.0.0.1:8096/healthz
curl -fsS http://127.0.0.1:8090/healthz
curl -fsS http://127.0.0.1:8099/healthz
curl -fsS http://127.0.0.1:8097/healthz
```

每项都应返回：

```json
{"ok":true}
```

验证直接访问 Web UI 已经不能伪造身份：

```bash
curl -sS http://127.0.0.1:8096/me
```

期望：

```json
{"error":"sign in","mode":"portal","reason":"unauthenticated"}
```

验证旧 Dev 登录接口已经关闭：

```bash
curl -sS \
  -X POST \
  -H 'content-type: application/json' \
  --data '{"user":"fake@example.com"}' \
  http://127.0.0.1:8096/signin
```

期望返回 `not_found`，而不是成功设置用户 Cookie。

---

## 12. 第一次通过邮件登录

浏览器打开：

```text
http://127.0.0.1:8097
```

操作流程：

1. Portal 发现没有 Session；
2. 跳转到 `/auth/login`；
3. Portal 创建 OIDC `state`、`nonce`、PKCE Challenge；
4. 跳转到 `/idp/authorize`；
5. 页面显示 `Enter your work email`；
6. 输入白名单中的邮箱；
7. 点击发送；
8. 页面无论邮箱是否允许，都会显示相似确认文字，避免泄漏白名单；
9. 到邮箱收件箱和垃圾邮件目录查找登录邮件；
10. 在发起登录的同一个浏览器 Profile 中打开链接；
11. Auth 验证一次性链接；
12. Portal 完成 `/auth/callback`；
13. Portal 创建签名 Session；
14. Web UI `/me` 返回真实邮箱身份。

一次性链接特性：

- 默认大约 15 分钟有效；
- 只能使用一次；
- 已使用链接再次打开会失败；
- Postgres 会保存防重放声明，重启服务不会让旧链接复活；
- 如果失败，回到登录页重新申请，不要重复使用旧链接。

### 12.1 “注册”到底发生了什么

QM 内置 Auth 没有传统的注册表单、用户名和密码。

第一次成功验证邮箱时：

- 邮箱成为稳定 Principal；
- QM 以它识别该用户；
- 该用户随后拥有自己的 `personal:<email>` Scope；
- 私人聊天、Memory、文件、Cron、Keychain、沙箱等都按 Principal/Scope 隔离。

因此准确说法是：

> 管理员先允许邮箱，用户第一次通过邮件链接登录后即时建立身份。

---

## 13. Resend：单邮箱测试与真正多用户的区别

### 13.1 单邮箱快速测试

未验证自有域名时，可以配置：

```dotenv
AUTH_EMAIL_FROM="QM <onboarding@resend.dev>"
```

但 Resend 测试发送通常只能投递到 Resend 账号自己的邮箱。这适合验证一个管理员邮箱的完整链路。

### 13.2 真正给多个用户发邮件

需要在 Resend：

1. 添加自己控制的域名或子域名，例如 `auth.example.com`；
2. 按页面提示添加 SPF/DKIM DNS 记录；
3. 等待状态变为 `verified`；
4. 把 QM 发件地址改为已验证域名：

```dotenv
AUTH_EMAIL_FROM="QM <login@auth.example.com>"
```

Resend 验证域名后，`login@auth.example.com` 不一定需要真实邮箱账户，它主要作为发件身份。

修改发件地址或 API Key 后，需要重启 Auth。

---

## 14. 将不同用户邮箱加入白名单

假设要允许：

```text
admin@example.com
alice@gmail.com
bob@outlook.com
```

编辑根 `.env` 中两处：

```dotenv
AUTH_ALLOWED_EMAILS=admin@example.com,alice@gmail.com,bob@outlook.com
OIDC_ALLOWED_EMAILS=admin@example.com,alice@gmail.com,bob@outlook.com
```

要求：

- 全部写成小写；
- 使用英文逗号；
- 不要出现中文逗号；
- 不要漏掉原管理员邮箱；
- Auth 与 OIDC 两份列表必须保持一致。

然后只重启：

```text
Auth :8099
Portal :8097
```

不需要重启 Core、Web UI 或 Postgres。

### 14.1 使用整个公司域名

如果所有合法用户都来自同一企业域名，可以改用：

```dotenv
AUTH_ALLOWED_EMAIL_DOMAIN=example.com
OIDC_ALLOWED_EMAIL_DOMAIN=example.com
```

使用域名策略时，建议删除或注释掉两条 `*_ALLOWED_EMAILS`，避免后续维护两套相互矛盾的边界。

### 14.2 新用户默认权限

白名单只代表：

```text
允许该邮箱证明身份并登录 QM
```

它不代表：

- 管理员；
- 可以查看其他人的私人聊天；
- 可以查看其他人的 Keychain；
- 自动加入所有共享项目；
- 可以修改组织配置。

新邮箱默认是普通用户。

---

## 15. 设置管理员

### 15.1 第一次初始化管理员

首次启动一个空数据库前配置：

```dotenv
ADMIN_GRANTS=admin@example.com:org_admin
```

Core 第一次看到空 `admin_grants` 存储时，会写入该种子。

### 15.2 为什么以后修改 `.env` 可能不生效

`ADMIN_GRANTS` 是一次性种子，不是每次启动都覆盖数据库的静态列表。

数据库已经存在管理员记录后：

- 修改 `ADMIN_GRANTS` 不会自动覆盖运行时授权；
- 应进入 Admin Dashboard 的 **Users** 页面提升或撤销管理员；
- 所有授权变更由 Core 审计；
- 系统会保护最后一个组织管理员，避免把组织锁死。

### 15.3 打开 Admin Dashboard

登录管理员邮箱后访问：

```text
http://127.0.0.1:8097/admin/
```

检查数据库中的管理员记录：

```bash
docker exec qm-auth-postgres \
  psql -U postgres -d qm -Atc \
  "select principal_id, role, scope_id from admin_grants order by principal_id;"
```

示例：

```text
admin@example.com|org_admin|org:local
```

---

## 16. 启用并理解 Keychain

Keychain 不是用户注册功能。它保存的是当前用户允许 Agent 使用的外部凭据，例如：

- API Key；
- Access Token；
- OAuth 账号；
- CLI 登录文件；
- 授权给某个共享 Scope 的凭据 Grant。

启用条件：

```dotenv
CONNECTOR_SECRET_KEY=<独立强密钥>
```

如果缺少它：

- `/api/keychain/overview` 会返回 `404 not_found`；
- 页面可能显示 `not_found`；
- Create secure form 无法真正保存凭据。

添加 `CONNECTOR_SECRET_KEY` 后必须重启 Core。

每个用户的 Keychain 按邮箱 Principal 隔离。A 用户保存的凭据不会自动出现在 B 用户的 Keychain 中。

---

## 17. 多用户隔离测试清单

使用两个独立 Chrome Profile，不要只使用同一 Profile 的两个标签页。

### 17.1 身份测试

用户 A 和用户 B 分别登录后，在各自会话中检查 `/me`：

```text
A → user = alice@example.com
B → user = bob@example.com
```

### 17.2 私人聊天

1. A 创建名称明显的私人会话；
2. B 刷新会话列表；
3. B 不应看到 A 的会话；
4. B 即使知道 A 的 Session ID，直接请求也应得到 `403` 或 `404`。

### 17.3 Personal Memory

1. A 写入唯一测试标记；
2. B 打开个人 Memory；
3. B 不应看到 A 的标记。

Org Memory 是组织共享内容，双方看到属于正常行为。

### 17.4 文件

1. A 上传一个私人文件；
2. B 不应在私人文件列表看到；
3. B 不应能够直接读取文件 ID。

### 17.5 Skills

- Personal Skill：只有所有者可见/可管理；
- Org Skill：组织成员可见；
- `/admin` Skill 可见不代表用户拥有管理员权限；
- 实际管理调用仍由 Core 检查 `admin_grants`。

### 17.6 Keychain

1. A 保存一项测试凭据；
2. B 的 Stored credentials 应保持为 0；
3. B 不能通过猜测 Credential ID 使用 A 的凭据；
4. 只有 A 明确创建 Grant 后，指定共享 Scope 才能使用；
5. 撤销 Grant 后应立即失效。

### 17.7 Admin 边界

- 管理员邮箱进入 `/admin/` 应成功；
- 普通用户访问 `/admin/` 应被拒绝；
- 普通用户即使能看到 `/admin` Skill，也不能调用管理 API。

---

## 18. 常见错误与排查

### 18.1 `Admin is temporarily unavailable`

含义通常不是管理员权限不足，而是 Admin 服务不可达。

检查：

```bash
lsof -nP -iTCP:8090 -sTCP:LISTEN
```

检查根 `.env`：

```dotenv
ADMIN_UPSTREAM=http://127.0.0.1:8090
```

确保：

1. Admin 插件已经启动；
2. `8090` 正在监听；
3. Portal 已经在加入 `ADMIN_UPSTREAM` 后重启。

### 18.2 Keychain 页面显示 `not_found`

最常见原因：

```dotenv
CONNECTOR_SECRET_KEY
```

未配置。加入独立密钥并重启 Core。

### 18.3 浏览器仍显示 Dev Principal 输入框

检查：

```dotenv
ALLOW_UNSIGNED_TEST_IDENTITY=0
NODE_ENV=production
CORE_SIGNING_SECRET=<已配置>
```

然后重启 Web UI。

### 18.4 访问 Portal 仍自动变成 `local-user`

说明 Portal 仍启用了：

```dotenv
PORTAL_LOCAL_AUTH_BYPASS=1
```

删除该变量并重启 Portal。

### 18.5 邮件没有收到

依次检查：

1. 输入邮箱是否完全小写并在白名单中；
2. `AUTH_ALLOWED_EMAILS` 与 `OIDC_ALLOWED_EMAILS` 是否一致；
3. 垃圾邮件目录；
4. Auth Terminal 是否出现发送失败日志；
5. Resend API Key 是否有效；
6. `AUTH_EMAIL_FROM` 是否来自 Resend 已验证域名；
7. 未验证域名时，收件人是否就是 Resend 账号自己的邮箱；
8. Resend Dashboard 的 Email Logs。

### 18.6 邮件链接提示已过期或无效

可能原因：

- 链接超过 TTL；
- 链接已经使用过；
- 在错误浏览器 Profile 打开；
- Portal Session Secret 被更换；
- Auth Signing JWK 或 Token Secret 被更换；
- Portal/Auth 的 Issuer、Redirect URI 不一致。

回到同一浏览器重新申请新链接。

### 18.7 `403 admin grant required`

检查当前邮箱是否真的存在于数据库 `admin_grants`，不要只检查 `.env`。

```bash
docker exec qm-auth-postgres \
  psql -U postgres -d qm -Atc \
  "select principal_id, role, scope_id from admin_grants;"
```

### 18.8 Core 启动时要求 `CONNECTOR_SECRET_KEY`

只要设置了 `DATABASE_URL`，QM 当前实现就要求持久化加密密钥：

```dotenv
CONNECTOR_SECRET_KEY=<独立强密钥>
```

该密钥不能等于 Core、Capability 或 Portal Identity Secret。

### 18.9 Core 日志仍显示 `store=memory`

检查：

```dotenv
DATABASE_URL=postgresql://postgres@127.0.0.1:5432/qm
SESSION_STORE=postgres
RUN_STORE=postgres
```

确认 Postgres 正常后重启 Core。

---

## 19. 日常启动、停止与备份

### 19.1 日常启动顺序

```bash
docker start qm-auth-postgres
```

然后按本指南第 10 节启动 Core、Web UI、Auth、Admin、Portal。

### 19.2 查看监听端口

```bash
lsof -nP \
  -iTCP:8080 \
  -iTCP:8090 \
  -iTCP:8096 \
  -iTCP:8097 \
  -iTCP:8099 \
  -sTCP:LISTEN
```

### 19.3 停止服务

在各 Terminal 中使用 `Ctrl+C`，顺序建议：

```text
Portal → Admin → Auth → Web UI → Core
```

停止数据库：

```bash
docker stop qm-auth-postgres
```

不要删除 `qm-auth-postgres-data`，否则持久化数据会丢失。

### 19.4 数据库备份

```bash
docker exec qm-auth-postgres \
  pg_dump -U postgres -d qm -Fc \
  > qm-backup.dump
```

备份文件可能包含私人会话、Memory、权限和凭据密文，应视为敏感文件。

---

## 20. 测试完成后删除或轮换 Resend API Key

如果 API Key 曾经出现在聊天、截图或日志中，应在 Resend Dashboard 撤销。

撤销后：

1. 新的登录邮件无法发送；
2. 已建立的 Portal Session 可能在过期前继续有效；
3. 若要继续使用邮件登录，创建新 Key；
4. 更新根 `.env`：

```dotenv
RESEND_API_KEY=<NEW_KEY>
```

5. 重启 Auth；
6. 不需要重启 Core、Web UI、Admin 或 Postgres。

再次确认密钥没有进入 Git：

```bash
git status --short
git check-ignore -v .env
git check-ignore -v plugins/web-ui/.env
```

不要运行会把 `.env` 强制加入 Git 的命令。

---

## 21. 从本机测试升级为生产部署

本机配置不能直接公开到互联网。生产至少需要完成：

1. 使用正式域名，例如 `https://qm.example.com`；
2. 配置有效 TLS 证书；
3. Portal/Auth 使用 `NODE_ENV=production`；
4. `PORTAL_PUBLIC_URL`、`AUTH_ISSUER`、`AUTH_REDIRECT_URI` 全部改为 HTTPS 正式域名；
5. PostgreSQL 使用强密码、私有网络、备份与监控；
6. 不使用 `POSTGRES_HOST_AUTH_METHOD=trust`；
7. Resend 使用已验证域名；
8. 使用进程管理器、Docker Compose、Fly.io 或 AWS，而不是手动开 Terminal；
9. Admin 服务只允许 Portal 私网访问；
10. 轮换所有本机测试期间暴露过的密钥；
11. 设置合理预算、限流和审计策略；
12. 用两个真实账号重新执行多用户隔离测试。

QM 官方更推荐生产组织创建独立 Deployment Repository，并通过 QM CLI 初始化：

```bash
npm exec --yes --package=@yc-software/qm@latest -- \
  qm init . --org <ORG_SLUG> --target <fly-or-aws>
npm install
```

然后使用：

```bash
npm exec qm -- setup
```

CLI 会生成 Auth Signing JWK、Token Secret、Client Secret 和 Portal OIDC 派生配置，减少手工出错概率。

---

## 22. 最终验收清单

### 环境

- [ ] Node `>=24.15.0`
- [ ] npm `>=11.10.0`
- [ ] Docker Engine 可用
- [ ] `qm-sandbox-local:latest` 已构建
- [ ] PostgreSQL `5432` 就绪

### Core 与持久化

- [ ] Core 日志显示 `store=postgres`
- [ ] Core 日志显示 `runStore=postgres`
- [ ] `CONNECTOR_SECRET_KEY` 已配置且与其他 Secret 不同
- [ ] Keychain 不再显示 `not_found`

### 身份

- [ ] `PORTAL_LOCAL_AUTH_BYPASS` 未启用
- [ ] `ALLOW_UNSIGNED_TEST_IDENTITY=0`
- [ ] 直接请求 Web UI `/me` 返回 `mode=portal`
- [ ] Portal 跳转到邮箱登录页面
- [ ] 白名单邮箱能收到一次性链接
- [ ] 链接只能使用一次
- [ ] 登录后 `/me` 返回正确邮箱

### 多用户

- [ ] Auth 与 Portal 白名单一致
- [ ] 两个邮箱使用独立浏览器 Profile 登录
- [ ] 私人会话互不可见
- [ ] Personal Memory 互不可见
- [ ] 私人文件互不可见
- [ ] Keychain 互不可见
- [ ] 共享 Scope 只对成员可见

### 管理员

- [ ] 管理员记录存在于 Postgres
- [ ] `/admin/` 可以打开
- [ ] 普通用户不能进入 Admin Dashboard
- [ ] `ADMIN_UPSTREAM=http://127.0.0.1:8090`
- [ ] Admin `8090` 未直接暴露到公网

### 安全

- [ ] `.env` 和插件 `.env` 被 Git 忽略
- [ ] 文档、聊天、截图中没有有效生产密钥
- [ ] 暴露过的 Resend Key 已撤销
- [ ] 生产环境已切换 HTTPS
- [ ] 生产数据库不使用 `trust`

---

## 结论

QM 的真正多用户不是在 Dev 页面输入不同 Principal，而是：

```text
可信邮箱验证
  + Portal 签名身份
  + Core 实时授权
  + Postgres 持久化
  + Personal/Shared Scope
  + 独立 Keychain 与 Sandbox
```

白名单解决“谁可以登录”，`admin_grants` 解决“谁可以治理组织”，Scope Membership 解决“谁可以访问共享项目”，Keychain Grant 解决“Agent 在什么上下文可以使用谁的凭据”。这四层不能混为一谈。

