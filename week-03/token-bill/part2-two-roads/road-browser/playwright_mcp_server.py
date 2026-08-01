# Week 3 · Exercise 2, Part 2 — Josep Coll
"""
A minimal Playwright MCP server — road two.

The exercise calls for `npx -y @playwright/mcp@latest` mounted in an MCP-capable
agent. This machine is WSL with no working Node toolchain and no OpenCode, so I
wrote the smallest server that reproduces the thing being measured: the same
four core tools the official server exposes (navigate, snapshot, type, click),
the same accessibility-tree snapshot format with `[ref=eN]` handles, over the
same stdio JSON-RPC transport, mounted in the course's own MCP agent loop.

Two honest caveats, both in the browser road's favour:
  * the official server advertises ~20 tools; mine advertises 4, so MY registry
    tax is far SMALLER than the real one;
  * my forum page is tiny next to a real Àrtemis page, so my snapshots are far
    SMALLER too.
Whatever ratio comes out of this is therefore a floor, not a ceiling.

    uv run --with mcp --with playwright python playwright_mcp_server.py
"""
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

mcp = FastMCP("playwright-min")

_state = {"pw": None, "browser": None, "page": None}

# The JS that turns the live DOM into the compact tree the model reads. Same
# idea as the official server: role, accessible name, and a ref handle the
# other tools can act on.
SNAPSHOT_JS = """() => {
  const roleOf = (el) => {
    const t = el.tagName.toLowerCase();
    if (t === 'a') return 'link';
    if (t === 'button') return 'button';
    if (t === 'textarea') return 'textbox';
    if (t === 'input') return (el.type === 'submit') ? 'button' : 'textbox';
    if (/^h[1-6]$/.test(t)) return 'heading';
    if (t === 'li') return 'listitem';
    if (t === 'p') return 'paragraph';
    if (t === 'nav') return 'navigation';
    if (t === 'form') return 'form';
    if (t === 'label') return 'label';
    return null;
  };
  const nameOf = (el) => {
    if (el.tagName.toLowerCase() === 'textarea' || el.tagName.toLowerCase() === 'input') {
      const lab = el.id ? document.querySelector(`label[for="${el.id}"]`) : null;
      return (lab ? lab.textContent : el.getAttribute('placeholder') || el.name || '').trim();
    }
    return (el.textContent || '').trim().replace(/\\s+/g, ' ').slice(0, 120);
  };
  // static text the page shows but that carries no interactive role — an
  // accessibility tree lists it, and without it the agent cannot read back
  // what it just posted.
  const ownText = (el) => Array.from(el.childNodes)
      .filter(n => n.nodeType === 3).map(n => n.textContent).join(' ')
      .trim().replace(/\\s+/g, ' ');
  const out = [];
  let n = 0;
  const walk = (el, depth) => {
    const role = roleOf(el);
    let d = depth;
    if (role) {
      n += 1;
      el.setAttribute('data-mcp-ref', 'e' + n);
      const name = nameOf(el);
      const extra = (el.tagName.toLowerCase() === 'textarea' || el.tagName.toLowerCase() === 'input')
        ? ` value="${(el.value || '').slice(0, 60)}"` : '';
      out.push('  '.repeat(depth) + `- ${role} "${name}"${extra} [ref=e${n}]`);
      d = depth + 1;
    } else {
      const t = ownText(el);
      if (t) out.push('  '.repeat(depth) + `- text "${t.slice(0, 160)}"`);
    }
    for (const child of el.children) walk(child, d);
  };
  walk(document.body, 0);
  return `- page url: ${location.href}\\n- page title: ${document.title}\\n` + out.join('\\n');
}"""


async def _page():
    if _state["page"] is None:
        _state["pw"] = await async_playwright().start()
        _state["browser"] = await _state["pw"].chromium.launch()
        _state["page"] = await _state["browser"].new_page()
    return _state["page"]


@mcp.tool()
async def browser_navigate(url: str) -> str:
    """Navigate the browser to a URL and return a snapshot of the page that
    loaded. Use this first, before any other browser tool."""
    page = await _page()
    await page.goto(url, wait_until="load")
    return await page.evaluate(SNAPSHOT_JS)


@mcp.tool()
async def browser_snapshot() -> str:
    """Capture an accessibility snapshot of the current page: every element the
    model can act on, with its role, its visible name and a [ref=eN] handle.
    Take a fresh snapshot after anything that changes the page."""
    page = await _page()
    return await page.evaluate(SNAPSHOT_JS)


async def _act(page, coro, what: str) -> str:
    """Run one page action and always come back with a FRESH snapshot.

    Refs are handed out by the last snapshot and die the moment the page
    navigates — submitting a form is exactly that. Without this, a stale ref
    fails with a bare timeout and the agent has nothing to steer by, so it
    retries the dead ref forever. The official Playwright MCP behaves the way
    this does: report the failure *and* hand back the current page.
    """
    try:
        await coro
        await page.wait_for_load_state("load")
        return await page.evaluate(SNAPSHOT_JS)
    except Exception as e:
        snap = await page.evaluate(SNAPSHOT_JS)
        return (f"{what} FAILED: {type(e).__name__}. The ref may be stale — the page has "
                f"changed since your last snapshot. Here is the page as it is NOW; use "
                f"these refs:\n{snap}")


@mcp.tool()
async def browser_type(ref: str, text: str) -> str:
    """Type text into an editable element of the page. `ref` is the [ref=eN]
    handle of the element as it appears in the latest snapshot, for example
    'e12'. Returns a fresh snapshot so you can check what was typed."""
    page = await _page()
    return await _act(page, page.fill(f'[data-mcp-ref="{ref}"]', text, timeout=5000),
                      f"browser_type({ref})")


@mcp.tool()
async def browser_click(ref: str) -> str:
    """Click an element of the page. `ref` is the [ref=eN] handle of the element
    as it appears in the latest snapshot, for example 'e13'. Returns a snapshot
    of whatever page the click led to."""
    page = await _page()
    return await _act(page, page.click(f'[data-mcp-ref="{ref}"]', timeout=5000),
                      f"browser_click({ref})")


if __name__ == "__main__":
    mcp.run()  # stdio transport (JSON-RPC over stdin/stdout)
