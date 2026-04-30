# Meego 工作项业务线字段查询说明

> 本文档供 Agent 学习使用，描述如何通过 Meego MCP 获取指定看板（视图）中所有工作项的业务线信息。

---

## 1. 概述

**目标**：给定一个 Meego 看板 URL，获取其中所有工作项的「业务线」字段值。

**业务线字段**：
- **字段 key**：`business`
- **字段类型**：`cascade_key_label_value`（级联选择树）
- **数据结构**：层级树，通常为 `一级业务线 / 二级业务线` 两级

---

## 2. 调用方式

### 底层通道

通过 **Meego MCP 服务**调用，服务名为 `meego_btd`。

使用命令行工具 `@lark-project/meego-mcporter` 发起调用：

```bash
npx @lark-project/meego-mcporter call meego_btd <tool_name> --config meego-config.json --args '<json>'
```

- **不是**直接调用 MCP API（如 REST/gRPC）
- **不是**通过飞书开放平台 OpenAPI
- **不是**使用 gdpa-cli

而是通过 mcporter 这个 CLI 工具包装 MCP 调用。

### 凭证

- 凭证文件：`~/.mcporter/credentials.json`（OAuth token，自动缓存）
- 配置文件：工作目录下的 `meego-config.json`（包含 MCP 服务连接信息）

---

## 3. 请求链路（两步）

### Step 1：从看板 URL 提取参数，查询视图获取工作项列表

**URL 格式**：
```
https://meego.larkoffice.com/<simple_name>/storyView/<view_id>?scope=workspaces&node=<node_id>
```

示例：
```
https://meego.larkoffice.com/pnsi/storyView/IiorbuNvg?scope=workspaces&node=64322503
```

提取：
- `simple_name` = `pnsi`（空间标识，MQL 中 `FROM` 子句的表名）
- `view_id` = `IiorbuNvg`（视图 ID）
- `project_key` = URL path 第一段，即 `pnsi`（与 simple_name 相同）

**调用工具**：`get_view_detail`

**请求**：
```bash
npx @lark-project/meego-mcporter call meego_btd get_view_detail \
  --config meego-config.json \
  --args '{"project_key": "pnsi", "view_id": "IiorbuNvg", "page_num": 1}'
```

**返回**：工作项列表，包含 `work_item_id` 和 `name`。每页最多 200 条，用 `page_num` 分页。

**示例返回**：
```
共查询到 14 条结果
| 需求标题 | 工作项 ID |
| MQ-Storage 新架构支持Texas/Clover | 6792921683 |
| [tt/nontt] 混布tlb集群沟通 | 6793396785 |
| ...
```

---

### Step 2：用 MQL 批量查询业务线字段值

**调用工具**：`search_by_mql`

**请求**：
```bash
npx @lark-project/meego-mcporter call meego_btd search_by_mql \
  --config meego-config.json \
  --args '{"project_key": "pnsi", "mql": "SELECT work_item_id, name, business FROM `pnsi`.`story` WHERE work_item_id IN (6792921683,6793396785,...) LIMIT 50"}'
```

**MQL 语法说明**：
- `SELECT work_item_id, name, business` — 查询字段
- `FROM \`pnsi\`.\`story\`` — 空间名.工作项类型（反引号包裹）
- `WHERE work_item_id IN (...)` — 按 ID 过滤
- `LIMIT 50` — 每页最多 50 条

**返回的 business 字段结构**：
```json
{
  "key": "business",
  "name": "业务线",
  "value_type": "cascade_key_label_value",
  "value": {
    "cascade_key_label_value": {
      "key": "65f90b75c07dc001a6be0290",
      "label": "Data Protection",
      "children": [
        {
          "key": "660389a9ac59d9842c6d7523",
          "label": "DES",
          "children": null
        }
      ]
    }
  }
}
```

- `label`：业务线显示名称
- `key`：业务线 option_id（用于写入时使用）
- `children`：下级业务线

---

## 4. 为什么不用其他方式

| 方式 | 说明 |
|------|------|
| `get_workitem_brief` 批量 | 只能查单个工作项，不支持一次传多个 ID + 指定字段 |
| MQL `WHERE business = "xxx"` | MQL 不支持 `_business`（cascade 类型）的等值筛选，只能用 `IS NULL / IS NOT NULL` |
| Open API | 有独立认证体系（app_id/app_secret），与 MCP OAuth token 不通用 |

所以最佳方案是：**先通过视图/ID列表拿到工作项 ID，再用 MQL 查询业务线字段值**。

---

## 5. 常见业务线树结构示例

```
Data Protection（一级）
├── DES（二级）
├── DECC（二级）
├── DAC（二级）
└── Data Protection-Others（二级）
```

每个节点都有 `key`（option_id）和 `label`（显示名），层级通过 `children` 数组嵌套。

---

## 6. Agent 实战速查

```
输入：Meego 看板 URL
  ↓
解析 URL → simple_name, view_id, project_key
  ↓
get_view_detail(project_key, view_id) → 工作项 ID 列表
  ↓
search_by_mql(SELECT work_item_id, name, business FROM `simple_name`.`story` WHERE work_item_id IN (...)) → 业务线数据
  ↓
解析 cascade_key_label_value → 输出结构化结果
```
