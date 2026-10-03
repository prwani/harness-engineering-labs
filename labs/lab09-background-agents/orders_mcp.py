"""A tiny, dependency-free MCP server over stdio with synthetic orders.

It speaks just enough JSON-RPC 2.0 (initialize, tools/list, tools/call)
to show how an external tool plugs into a harness. All data is fake.

Register it from the app folder:
    harness mcp add orders -- python /absolute/path/to/orders_mcp.py
"""
import json
import sys

ORDERS = [
    {"id": "ORD-1001", "status": "shipped", "lines": [{"sku": "P1", "qty": 2}]},
    {"id": "ORD-1002", "status": "pending", "lines": [{"sku": "P2", "qty": 4}, {"sku": "P3", "qty": 1}]},
    {"id": "ORD-1003", "status": "pending", "lines": [{"sku": "P1", "qty": 400}]},
    {"id": "ORD-1004", "status": "cancelled", "lines": [{"sku": "P4", "qty": 900}]},
    {"id": "ORD-1005", "status": "pending", "lines": [{"sku": "P5", "qty": 750}, {"sku": "P2", "qty": 2}]},
]

TOOLS = [
    {
        "name": "list_orders",
        "description": "List synthetic pet-store orders, optionally filtered by status (pending, shipped, cancelled).",
        "inputSchema": {
            "type": "object",
            "properties": {"status": {"type": "string", "enum": ["pending", "shipped", "cancelled"]}},
        },
    },
    {
        "name": "get_order",
        "description": "Get one synthetic order by id, e.g. ORD-1002.",
        "inputSchema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
]


def call_tool(name, args):
    if name == "list_orders":
        status = args.get("status")
        return [o for o in ORDERS if status in (None, o["status"])]
    if name == "get_order":
        for order in ORDERS:
            if order["id"] == args.get("order_id"):
                return order
        raise ValueError(f"no order {args.get('order_id')!r}")
    raise ValueError(f"unknown tool {name!r}")


def reply(msg_id, result=None, error=None):
    body = {"jsonrpc": "2.0", "id": msg_id}
    body["error" if error else "result"] = error or result
    sys.stdout.write(json.dumps(body) + "\n")
    sys.stdout.flush()


for raw in sys.stdin:
    if not raw.strip():
        continue
    msg = json.loads(raw)
    method, msg_id = msg.get("method"), msg.get("id")
    if msg_id is None:  # notifications need no reply
        continue
    if method == "initialize":
        reply(msg_id, {
            "protocolVersion": msg.get("params", {}).get("protocolVersion", "2024-11-05"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "orders", "version": "0.1.0"},
        })
    elif method == "tools/list":
        reply(msg_id, {"tools": TOOLS})
    elif method == "tools/call":
        params = msg.get("params", {})
        try:
            data = call_tool(params.get("name"), params.get("arguments") or {})
            reply(msg_id, {"content": [{"type": "text", "text": json.dumps(data, indent=2)}]})
        except ValueError as exc:
            reply(msg_id, {"content": [{"type": "text", "text": str(exc)}], "isError": True})
    elif method == "ping":
        reply(msg_id, {})
    else:
        reply(msg_id, error={"code": -32601, "message": f"method not found: {method}"})
