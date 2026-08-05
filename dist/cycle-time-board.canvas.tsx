import {
  Stack, Row, Grid, H1, H2, H3, Text, Card, CardHeader, CardBody,
  Table, Stat, Callout, Pill, Divider, Link, Spacer, PieChart, Button,
  useHostTheme, useCanvasState, useCanvasAction,
} from "cursor/canvas";

// ── Palette ───────────────────────────────────────────────────────────────────
// Extracted from brand swatch: blush · lavender · mint · grey · charcoal
const P = {
  blush:    "#fff0f8",
  lavender: "#ebe0fc",
  mint:     "#d4f5ee",
  grey:     "#707070",
  charcoal: "#333333",
  // Derived accent shades
  lavenderDeep: "#c4a8f5",
  mintDeep:     "#52c5ad",
  blushBorder:  "#e8c8e0",
};

// ── Data ─────────────────────────────────────────────────────────────────────

type Status = "Todo" | "In Progress" | "Ready for Review" | "Done" | "Closed";

type PRSummary = {
  problem: string;
  solution: string;
  keyChanges: string[];
  prType: string;
};

type Issue = {
  number: number;
  title: string;
  url: string;
  status: Status;
  sprint: string;
  labels: string[];
  assignedAt: string;
  /** when the issue was first placed into "Todo" on the project board */
  todoAt: string;
  /** when the issue moved from "Todo" → "In Progress" on the project board */
  inProgressAt?: string;
  prNumber?: number;
  prTitle?: string;
  prUrl?: string;
  prCreatedAt?: string;
  mergedAt?: string;
  /** hours from assigned → merged (undefined if still open) */
  cycleHours?: number;
  /** hours from PR open → merged */
  prOpenHours?: number;
  /** summary extracted from the PR description */
  prSummary?: PRSummary;
};

const ISSUES: Issue[] = [
  {
    "number": 625,
    "title": "Fix hardcoded user-facing strings across policy and resource action hooks",
    "url": "https://github.com/Kuadrant/kuadrant-console-plugin/issues/625",
    "status": "In Progress",
    "sprint": "Sprint 38",
    "labels": [
      "enhancement",
      "good first issue",
      "triage/accepted"
    ],
    "assignedAt": "2026-07-13T08:30:40Z",
    "todoAt": "2026-07-13T08:30:40Z",
    "inProgressAt": "2026-07-29T15:25:18Z"
  },
  {
    "number": 664,
    "title": "docs: create CI.md to document e2e pipeline design and decisions",
    "url": "https://github.com/Kuadrant/kuadrant-console-plugin/issues/664",
    "status": "Todo",
    "sprint": "Sprint 38",
    "labels": [
      "documentation",
      "good first issue",
      "triage/accepted"
    ],
    "assignedAt": "2026-07-22T10:22:56Z",
    "todoAt": "2026-07-22T10:22:56Z"
  },
  {
    "number": 651,
    "title": "Migrate to @openshift-console/dynamic-plugin-sdk 4.22.0",
    "url": "https://github.com/Kuadrant/kuadrant-console-plugin/issues/651",
    "status": "Todo",
    "sprint": "Sprint 38",
    "labels": [
      "dependencies",
      "epic",
      "triage/accepted",
      "sdk-maintenance"
    ],
    "assignedAt": "2026-07-15T10:55:08Z",
    "todoAt": "2026-07-15T15:45:47Z",
    "cycleHours": 482.9,
    "prOpenHours": 0.3,
    "prSummary": {
      "prType": "Pull Request",
      "problem": "",
      "solution": "Release v0.6.0",
      "keyChanges": []
    },
    "prNumber": 706,
    "prTitle": "v0.6.0",
    "prUrl": "https://github.com/Kuadrant/kuadrant-console-plugin/pull/706",
    "prCreatedAt": "2026-08-04T13:30:42Z",
    "mergedAt": "2026-08-04T13:49:37Z"
  },
  {
    "number": 637,
    "title": "Upgrade to React 18",
    "url": "https://github.com/Kuadrant/kuadrant-console-plugin/issues/637",
    "status": "Todo",
    "sprint": "Sprint 38",
    "labels": [
      "enhancement",
      "triage/accepted",
      "sdk-maintenance"
    ],
    "assignedAt": "2026-07-15T10:54:44Z",
    "todoAt": "2026-07-15T15:39:58Z"
  },
  {
    "number": 468,
    "title": "DNSPolicy ProviderRefs Empty String Bypass",
    "url": "https://github.com/Kuadrant/kuadrant-console-plugin/issues/468",
    "status": "Todo",
    "sprint": "Unassigned",
    "labels": [
      "bug",
      "good first issue",
      "triage/accepted"
    ],
    "assignedAt": "2026-07-29T10:45:57Z",
    "todoAt": "2026-07-29T10:45:57Z"
  },
  {
    "number": 614,
    "title": "API Product deletion type to confirm missing when deleting from details",
    "url": "https://github.com/Kuadrant/kuadrant-console-plugin/issues/614",
    "status": "Done",
    "sprint": "Sprint 37",
    "labels": [
      "enhancement",
      "good first issue",
      "triage/accepted",
      "maintainers-only"
    ],
    "assignedAt": "2026-07-08T11:43:52Z",
    "todoAt": "2026-07-08T11:44:25Z",
    "inProgressAt": "2026-07-17T08:50:45Z",
    "cycleHours": 334.0,
    "prOpenHours": 18.6,
    "prSummary": {
      "prType": "Bug Fix",
      "problem": "APIProduct detail page Actions dropdown used the SDK's built-in useDeleteModal (simple checkbox confirmation), while the list page kebab already used the custom type-to-confirm APIProductDeleteModal \u2014 inconsistent delete UX across views.",
      "solution": "Replaced useDeleteModal with the SDK's useModal hook to launch APIProductDeleteModal from the Actions dropdown, matching PatternFly's 'Confirm a destructive action' guidelines. Detail page now navigates back to the APIProducts list after successful deletion.",
      "keyChanges": [
        "Added optional onDeleteSuccess callback to APIProductDeleteModal so detail page can navigate away on success",
        "Moved setIsDeleting cleanup out of finally into catch only \u2014 avoids setState-on-unmount warnings",
        "Switched useAPIProductActions from useDeleteModal to useModal with APIProductDeleteModalWrapper",
        "Updated e2e delete flow to type the resource name into #confirm-delete instead of checking a checkbox"
      ]
    },
    "prNumber": 676,
    "prTitle": "Type-to-confirm APIProduct Actions Menu",
    "prUrl": "https://github.com/Kuadrant/kuadrant-console-plugin/pull/676",
    "prCreatedAt": "2026-07-21T15:09:04Z",
    "mergedAt": "2026-07-22T09:43:16Z"
  },
  {
    "number": 590,
    "title": "Details pages content heavily left-aligned",
    "url": "https://github.com/Kuadrant/kuadrant-console-plugin/issues/590",
    "status": "Done",
    "sprint": "Sprint 37",
    "labels": [
      "good first issue",
      "triage/accepted"
    ],
    "assignedAt": "2026-07-02T16:53:45Z",
    "todoAt": "2026-07-02T16:52:16Z",
    "inProgressAt": "2026-07-06T10:00:45Z",
    "cycleHours": 98.3,
    "prOpenHours": 2.7,
    "prSummary": {
      "prType": "Style / Formatting",
      "problem": "Header contents inside the DNS, TLS, and OIDC policy creation tabs were extremely left-aligned, mismatching the rest of the page layout.",
      "solution": "Identified a PatternFly `pf-m-no-padding` modifier class applied to the body wrapper of each policy header. Commenting it out restored correct alignment across all three policy pages.",
      "keyChanges": [
        "Commented out `pf-m-no-padding` class on DNS, TLS, and OIDC header wrappers",
        "No logic changes \u2014 pure layout fix",
        "Verified visually: headers now align with other page content"
      ]
    },
    "prNumber": 602,
    "prTitle": "Alignment Issue Fix",
    "prUrl": "https://github.com/Kuadrant/kuadrant-console-plugin/pull/602",
    "prCreatedAt": "2026-07-06T16:31:14Z",
    "mergedAt": "2026-07-06T19:11:11Z"
  },
  {
    "number": 583,
    "title": "Add GatewayClass filtering for gateway tables",
    "url": "https://github.com/Kuadrant/kuadrant-console-plugin/issues/583",
    "status": "Done",
    "sprint": "Sprint 38",
    "labels": [
      "enhancement",
      "triage/accepted",
      "maintainers-only"
    ],
    "assignedAt": "2026-07-09T14:09:42Z",
    "todoAt": "2026-07-09T14:09:42Z",
    "inProgressAt": "2026-07-29T14:56:44Z",
    "cycleHours": 503.8,
    "prOpenHours": 23.0,
    "prSummary": {
      "prType": "Feature",
      "problem": "Gateway tables showed all gateways including irrelevant types (e.g. waypoint gateways with gatewayClassName 'istio-waypoint'). Only Name, Namespace, and Type filters existed \u2014 no GatewayClass filter.",
      "solution": "Extended ResourceList with a reusable additionalFilters prop (PatternFly dropdown select), then wired a GatewayClass filter on the Overview 'Gateways - Traffic Analysis' card, populated dynamically from cluster GatewayClass resources.",
      "keyChanges": [
        "Added AdditionalFilter type and optional additionalFilters prop to ResourceList (default [])",
        "When an additional filter is active, toolbar text input switches to a Select dropdown with an All option",
        "Extended Gateway interface with spec.gatewayClassName; watch GatewayClass resources for dropdown options",
        "Passed GatewayClass filter into Overview gateway ResourceList comparing spec.gatewayClassName"
      ]
    },
    "prNumber": 698,
    "prTitle": "GatewayClass Filter Dropdown",
    "prUrl": "https://github.com/Kuadrant/kuadrant-console-plugin/pull/698",
    "prCreatedAt": "2026-07-29T14:56:44Z",
    "mergedAt": "2026-07-30T13:59:10Z"
  },
  {
    "number": 572,
    "title": "API Product deletion type to confirm UI enhancement",
    "url": "https://github.com/Kuadrant/kuadrant-console-plugin/issues/572",
    "status": "Done",
    "sprint": "Sprint 37",
    "labels": [
      "enhancement",
      "good first issue",
      "triage/accepted",
      "maintainers-only"
    ],
    "assignedAt": "2026-07-01T09:46:57Z",
    "todoAt": "2026-06-30T14:41:03Z",
    "inProgressAt": "2026-07-07T09:43:46Z",
    "cycleHours": 167.9,
    "prOpenHours": 17.9,
    "prSummary": {
      "prType": "Style / Formatting",
      "problem": "API Product and API Key deletion modals had inconsistent UI/UX \u2014 different sizes, layouts, and confirmation patterns between the two flows.",
      "solution": "Used the API Key modal as a consistent base and redesigned both modals to follow PatternFly's 'Confirm a destructive action' guidelines, unifying the experience across both resource types.",
      "keyChanges": [
        "Modal size reduced from medium \u2192 small for a more focused feel",
        "Added warning icon and simplified messaging to a single line",
        "Improved placeholder text: 'Enter API Product name' for better guidance",
        "Simplified confirm button label from 'Delete API Product' \u2192 'Delete'",
        "Added useEffect hook to reliably reset the confirmation field on all close methods (Cancel, ESC, click-outside)",
        "Reorganised imports to match project conventions; added kuadrant.css import"
      ]
    },
    "prNumber": 609,
    "prTitle": "APIProduct/Key Delete UI Enhance",
    "prUrl": "https://github.com/Kuadrant/kuadrant-console-plugin/pull/609",
    "prCreatedAt": "2026-07-07T15:44:26Z",
    "mergedAt": "2026-07-08T09:38:54Z"
  },
  {
    "number": 571,
    "title": "Cancel button navigates to resource list instead of previous page",
    "url": "https://github.com/Kuadrant/kuadrant-console-plugin/issues/571",
    "status": "Closed",
    "sprint": "Sprint 37",
    "labels": [
      "enhancement",
      "good first issue",
      "triage/accepted",
      "maintainers-only"
    ],
    "assignedAt": "2026-07-01T09:47:16Z",
    "todoAt": "2026-06-30T14:27:32Z",
    "inProgressAt": "2026-07-07T17:30:44Z",
    "cycleHours": 216.9,
    "prSummary": {
      "prType": "Closed \u2014 Won't Fix",
      "problem": "Cancel buttons on create/edit forms (policies, Gateways, HTTPRoutes \u2014 Form and YAML view) navigate to the resource list page instead of the previous page, breaking natural navigation flow.",
      "solution": "Closed as not technically feasible. The OpenShift Console SDK's ResourceYAMLEditor does not expose an onCancel prop or any way to customise the cancel button. A custom YAML editor wrapper would be fragile and unnecessary given the planned form view work.",
      "keyChanges": [
        "Custom YAML editor approach investigated and ruled out",
        "Textarea alternative considered and discarded",
        "Confirmed via SDK type definitions: cancel customisation is not supported",
        "Same broken behaviour found on HTTPRoutes and Gateway YAML creation",
        "Resolution deferred to upcoming form view redesign"
      ]
    },
    "mergedAt": "2026-07-10T10:40:43Z"
  }
];

function fmtDate(iso: string) {
  return iso.slice(0, 10);
}

function fmtTime(iso: string) {
  return iso.slice(11, 16) + " UTC";
}

function fmtHours(h: number): string {
  if (h < 24) return `${h.toFixed(1)}h`;
  const d = Math.floor(h / 24);
  const rem = h % 24;
  return rem < 1 ? `${d}d` : `${d}d ${rem.toFixed(0)}h`;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function LabelChip({ name }: { name: string }) {
  const theme = useHostTheme();
  const highlight = name === "maintainers-only";
  return (
    <span style={{
      fontSize: 10, padding: "1px 5px", borderRadius: 3,
      background: highlight ? theme.fill.tertiary : theme.fill.secondary,
      color: highlight ? theme.text.secondary : theme.text.tertiary,
      whiteSpace: "nowrap",
    }}>
      {name}
    </span>
  );
}

function StatusBadge({ status }: { status: Status }) {
  const cfg: Record<Status, { bg: string; color: string; fw?: number }> = {
    "Todo":            { bg: P.lavender,     color: P.charcoal },
    "In Progress":     { bg: "#f59e0b22",    color: "#b45309", fw: 600 },
    "Ready for Review":{ bg: P.mint,         color: "#0e7c65" },
    "Done":            { bg: P.mintDeep,     color: "#fff" },
    "Closed":          { bg: "#e0e0e0",      color: "#666" },
  };
  const { bg, color, fw } = cfg[status];
  return (
    <span style={{
      fontSize: 10, fontWeight: fw ?? 400,
      padding: "2px 7px", borderRadius: 3, whiteSpace: "nowrap",
      background: bg, color,
    }}>
      {status}
    </span>
  );
}

function TimelineBar({ issue }: { issue: Issue }) {
  const theme = useHostTheme();
  const NOW = new Date().toISOString();

  const todoMs       = new Date(issue.todoAt).getTime();
  const inProgMs     = issue.inProgressAt ? new Date(issue.inProgressAt).getTime() : null;
  const prMs         = issue.prCreatedAt  ? new Date(issue.prCreatedAt).getTime()  : null;
  const mergedMs     = issue.mergedAt     ? new Date(issue.mergedAt).getTime()     : null;
  const nowMs        = new Date(NOW).getTime();
  const endMs        = mergedMs ?? nowMs;
  const totalMs      = endMs - todoMs;

  // Segment widths as percentages of total span
  const todoPct   = inProgMs ? ((inProgMs - todoMs) / totalMs) * 100 : 100;
  const inProgEnd = prMs ?? mergedMs ?? nowMs;
  const inProgPct = inProgMs ? ((inProgEnd - inProgMs) / totalMs) * 100 : 0;
  const reviewPct = (prMs && mergedMs) ? ((mergedMs - prMs) / totalMs) * 100 : 0;

  const todoHrs    = inProgMs ? (inProgMs - todoMs) / 3_600_000 : (endMs - todoMs) / 3_600_000;
  const inProgHrs  = inProgMs ? (inProgEnd - inProgMs) / 3_600_000 : 0;
  const reviewHrs  = (prMs && mergedMs) ? (mergedMs - prMs) / 3_600_000 : 0;

  // Colours — palette-mapped
  const todoColor    = P.lavender;
  const inProgColor  = "#f59e0b";   // amber — "in progress"
  const reviewColor  = P.mintDeep;

  // Marker line at the Todo → In Progress boundary
  const markerPct = todoPct;

  return (
    <Stack gap={6}>
      {/* Bar */}
      <div style={{ position: "relative" }}>
        <div style={{
          height: 10, borderRadius: 5, background: theme.fill.tertiary,
          overflow: "visible", display: "flex",
        }}>
          {/* Todo segment */}
          <div title={`Todo: ${fmtHours(todoHrs)}`} style={{
            width: `${todoPct}%`, background: todoColor,
            borderRadius: inProgMs ? "5px 0 0 5px" : 5,
            transition: "width 0.3s",
          }} />
          {/* In Progress segment */}
          {inProgPct > 0 && (
            <div title={`In Progress: ${fmtHours(inProgHrs)}`} style={{
              width: `${inProgPct}%`, background: inProgColor,
              borderRadius: reviewPct > 0 ? "0" : "0 5px 5px 0",
            }} />
          )}
          {/* Review segment */}
          {reviewPct > 0 && (
            <div title={`Review: ${fmtHours(reviewHrs)}`} style={{
              width: `${reviewPct}%`, background: reviewColor,
              borderRadius: "0 5px 5px 0",
            }} />
          )}
          {/* Trailing pulse if still open */}
          {!mergedMs && (
            <div style={{ width: 6, background: inProgMs ? inProgColor : todoColor, opacity: 0.4, borderRadius: "0 3px 3px 0" }} />
          )}
          {/* Transition marker (vertical tick at Todo → In Progress) */}
          {inProgMs && (
            <div style={{
              position: "absolute", left: `${markerPct}%`,
              top: -3, bottom: -3, width: 2,
              background: inProgColor, borderRadius: 1,
            }} />
          )}
        </div>
      </div>

      {/* Phase labels row */}
      <div style={{ position: "relative", height: 32 }}>
        {/* Todo label — anchored to left */}
        <span style={{
          position: "absolute", left: 0,
          fontSize: 9, color: theme.text.tertiary,
          display: "flex", flexDirection: "column", alignItems: "flex-start",
        }}>
          <span style={{ fontWeight: 500, color: theme.text.secondary }}>Todo</span>
          <span>{fmtDate(issue.todoAt)}</span>
          <span style={{ color: theme.text.quaternary }}>{fmtHours(todoHrs)}</span>
        </span>

        {/* In Progress label — anchored at the transition marker */}
        {inProgMs && (
          <span style={{
            position: "absolute",
            left: `calc(${markerPct}% + 4px)`,
            fontSize: 9,
            display: "flex", flexDirection: "column", alignItems: "flex-start",
          }}>
            <span style={{ fontWeight: 600, color: inProgColor }}>▶ In Progress</span>
            <span style={{ color: theme.text.tertiary }}>{fmtDate(issue.inProgressAt!)}</span>
            {inProgHrs > 0 && (
              <span style={{ color: theme.text.quaternary }}>{fmtHours(inProgHrs)}</span>
            )}
          </span>
        )}

        {/* End label — anchored to right */}
        <span style={{
          position: "absolute", right: 0,
          fontSize: 9, color: theme.text.tertiary,
          display: "flex", flexDirection: "column", alignItems: "flex-end",
        }}>
          {mergedMs ? (
            <>
              <span style={{ fontWeight: 500, color: reviewColor }}>Merged</span>
              <span>{fmtDate(issue.mergedAt!)}</span>
              {reviewHrs > 0 && <span style={{ color: theme.text.quaternary }}>Review {fmtHours(reviewHrs)}</span>}
            </>
          ) : (
            <span style={{ fontStyle: "italic" }}>now…</span>
          )}
        </span>
      </div>

      {/* Colour legend */}
      <Row gap={10}>
        <Row gap={3} align="center">
          <div style={{ width: 8, height: 8, borderRadius: 2, background: todoColor }} />
          <Text size="small" tone="tertiary" style={{ fontSize: 9 }}>Todo</Text>
        </Row>
        {inProgMs && (
          <Row gap={3} align="center">
            <div style={{ width: 8, height: 8, borderRadius: 2, background: inProgColor }} />
            <Text size="small" tone="tertiary" style={{ fontSize: 9 }}>In Progress</Text>
          </Row>
        )}
        {reviewPct > 0 && (
          <Row gap={3} align="center">
            <div style={{ width: 8, height: 8, borderRadius: 2, background: reviewColor }} />
            <Text size="small" tone="tertiary" style={{ fontSize: 9 }}>Review</Text>
          </Row>
        )}
      </Row>
    </Stack>
  );
}

// ── Main ──────────────────────────────────────────────────────────────────────

// Unique filter values derived from data
const ALL_LABELS  = [...new Set(ISSUES.flatMap(i => i.labels))].sort();
const ALL_SPRINTS = [...new Set(ISSUES.map(i => i.sprint))].sort();

export default function UITouchGrassBoard() {
  const theme = useHostTheme();
  const [view, setView] = useCanvasState<"board" | "sprint" | "cycle">("view", "cycle");
  const [themeMode, setThemeMode] = useCanvasState<"light" | "dark">("themeMode", "light");
  const [expanded, setExpanded] = useCanvasState<number[]>("expanded", []);
  const [showOpenIssues, setShowOpenIssues] = useCanvasState<boolean>("showOpenIssues", true);
  const [showDoneIssues, setShowDoneIssues] = useCanvasState<boolean>("showDoneIssues", true);
  const toggleExpanded = (n: number) =>
    setExpanded(prev => prev.includes(n) ? prev.filter(x => x !== n) : [...prev, n]);

  // ── Filter state ────────────────────────────────────────────────────────────
  const [search,       setSearch]       = useCanvasState<string>("search",       "");
  const [filterLabel,  setFilterLabel]  = useCanvasState<string>("filterLabel",  "");
  const [filterSprint, setFilterSprint] = useCanvasState<string>("filterSprint", "");
  const [filterDate,   setFilterDate]   = useCanvasState<string>("filterDate",   "all");

  const NOW_MS  = Date.now();
  const DAY_MS  = 86_400_000;

  const filtered = ISSUES.filter(issue => {
    if (search && !issue.title.toLowerCase().includes(search.toLowerCase()) &&
        !String(issue.number).includes(search)) return false;
    if (filterLabel  && !issue.labels.includes(filterLabel))  return false;
    if (filterSprint && issue.sprint !== filterSprint)         return false;
    if (filterDate !== "all") {
      const ms = new Date(issue.todoAt).getTime();
      if (filterDate === "thisweek"  && ms < NOW_MS - 7  * DAY_MS) return false;
      if (filterDate === "last2weeks"&& ms < NOW_MS - 14 * DAY_MS) return false;
      if (filterDate === "older"     && ms >= NOW_MS - 14 * DAY_MS) return false;
    }
    return true;
  });

  const hasFilter   = search !== "" || filterLabel !== "" || filterSprint !== "" || filterDate !== "all";
  const clearAll    = () => { setSearch(""); setFilterLabel(""); setFilterSprint(""); setFilterDate("all"); };

  const filteredDone = filtered.filter(i => i.status === "Done" || i.status === "Closed");
  const OPEN_STATUS_ORDER: Status[] = ["In Progress", "Ready for Review", "Todo"];
  const filteredOpen = filtered
    .filter(i => i.status !== "Done" && i.status !== "Closed")
    .sort((a, b) => OPEN_STATUS_ORDER.indexOf(a.status) - OPEN_STATUS_ORDER.indexOf(b.status));
  const byStatusF    = (s: Status) => filtered.filter(i => i.status === s);

  const done      = ISSUES.filter(i => i.status === "Done");
  const resolved  = ISSUES.filter(i => i.status === "Done" || i.status === "Closed");
  const avgCycle  = resolved.reduce((s, i) => s + (i.cycleHours ?? 0), 0) / resolved.length;
  const avgPR     = done.reduce((s, i) => s + (i.prOpenHours ?? 0), 0) / done.length;

  const STATUS_ORDER: Status[] = ["Todo", "In Progress", "Ready for Review", "Done", "Closed"];

  function primaryCategory(issue: Issue): string {
    if (issue.labels.includes("enhancement")) return "Enhancement";
    if (issue.labels.includes("documentation")) return "Documentation";
    if (issue.labels.includes("bug")) return "Bug";
    if (issue.labels.includes("dependencies") || issue.labels.includes("epic")) return "Dependency/Epic";
    return "Uncategorized";
  }
  const pieData = (() => {
    const counts: Record<string, number> = {};
    for (const issue of ISSUES) {
      const c = primaryCategory(issue);
      counts[c] = (counts[c] ?? 0) + 1;
    }
    return Object.entries(counts)
      .filter(([, v]) => v > 0)
      .map(([label, value]) => ({ label, value }));
  })();
  const labelRows = (() => {
    const counts: Record<string, number> = {};
    for (const issue of ISSUES) {
      for (const l of issue.labels) counts[l] = (counts[l] ?? 0) + 1;
    }
    return Object.entries(counts).sort((a, b) => b[1] - a[1]);
  })();


  const dispatch = useCanvasAction();
  const REFRESH_PROMPT =
    "Using the cycle-time-board skill, refresh my personal board from GitHub " +
    "(python3 scripts/fetch.py && generate_html.py && generate_canvas.py) " +
    "and update the canvas with current statuses, PRs, and cycle times.";

  const inputBase = {
    display: "block" as const, width: "100%", boxSizing: "border-box" as const,
    padding: "7px 12px", borderRadius: 7,
    border: `1.5px solid ${themeMode === "dark" ? "#3d3548" : P.blushBorder}`,
    background: themeMode === "dark" ? "#24262b" : "#fff",
    fontSize: 13, color: themeMode === "dark" ? "#ececec" : P.charcoal,
    outline: "none",
  };
  const selectBase = {
    ...inputBase,
    appearance: "none" as const,
    WebkitAppearance: "none" as const,
    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%23707070'/%3E%3C/svg%3E")`,
    backgroundRepeat: "no-repeat" as const,
    backgroundPosition: "right 10px center",
    paddingRight: 28,
    cursor: "pointer" as const,
  };

  return (
    <Stack gap={20} style={{
      padding: 24, maxWidth: 1060, margin: "0 auto", minHeight: "100%",
      background: themeMode === "dark" ? "#1a1b1e" : "#f7f5f8",
      color: themeMode === "dark" ? "#ececec" : P.charcoal,
    }}>

      {/* Header */}
      <Row align="center" style={{ background: themeMode === "dark" ? "#3a2f52" : P.lavender, borderRadius: 10, padding: "16px 20px", marginBottom: -8 }}>
        <Stack gap={2} style={{ flex: 1 }}>
          <H1 style={{ color: themeMode === "dark" ? "#ececec" : P.charcoal }}>Example — Cycle Time</H1>
          <Text tone="secondary" size="small" style={{ color: P.grey }}>
            example-org/example-repo ·{" "}
            <Link href="https://github.com/orgs/example-org/projects/1">Project #1</Link>
            {" "}· Last fetched 2026-08-05
          </Text>
        </Stack>
        <Row gap={8} align="center" style={{ flexShrink: 0 }}>
          <Button onClick={() => setThemeMode(themeMode === "light" ? "dark" : "light")}>
            {themeMode === "light" ? "Dark mode" : "Light mode"}
          </Button>
          <Button onClick={() => dispatch({ type: "newComposerChat", userPrompt: REFRESH_PROMPT })}>
            Refresh from GitHub
          </Button>
        </Row>
      </Row>

      {/* Summary stats */}
      <Grid columns={4} gap={12}>
        <Stat value={ISSUES.length}         label="Issues assigned" />
        <Stat value={resolved.length}       label="Resolved" tone="success" />
        <Stat value={fmtHours(avgCycle)}    label="Avg assigned → resolved" />
        <Stat value={done.length > 0 ? fmtHours(avgPR) : "—"} label="Avg PR open → merged" />
      </Grid>

      <Divider />

      {/* Label breakdown — pie chart */}
      <Stack gap={12}>
        <Stack gap={2}>
          <H2>Issues by label type</H2>
          <Text tone="secondary" size="small">
            Each issue classified by its primary category label. Source: GitHub Labels · Sprints 37–38
          </Text>
        </Stack>
        <Grid columns="1fr 1fr" gap={24} align="start">
          <PieChart donut size={220} data={pieData} />
          <Stack gap={10}>
            <H3>All labels across issues</H3>
            <Table
              headers={["Label", "Issues"]}
              columnAlign={["left", "right"]}
              rows={labelRows.map(([label, count]) => [
                <Text size="small">{label}</Text>,
                <Text size="small" weight="semibold">{String(count)}</Text>,
              ])}
            />
          </Stack>
        </Grid>
      </Stack>

      <Divider />

      {/* ── Search & Filter bar ─────────────────────────────────────────────── */}
      <Stack gap={10}>
        {/* Search input */}
        <div style={{ position: "relative" }}>
          <span style={{
            position: "absolute", left: 11, top: "50%", transform: "translateY(-50%)",
            fontSize: 14, color: P.grey, pointerEvents: "none",
          }}>🔍</span>
          <input
            type="text"
            placeholder="Search issues by name or #number…"
            value={search}
            onChange={(e: { target: { value: string } }) => setSearch(e.target.value)}
            style={{ ...inputBase, paddingLeft: 32 }}
          />
        </div>

        {/* Filter row */}
        <Grid columns={3} gap={10}>
          {/* Date filter */}
          <Stack gap={3}>
            <Text size="small" style={{ fontSize: 10, fontWeight: 600, color: P.grey, letterSpacing: "0.06em", textTransform: "uppercase" as const }}>Date added</Text>
            <select
              value={filterDate}
              onChange={(e: { target: { value: string } }) => setFilterDate(e.target.value)}
              style={selectBase}
            >
              <option value="all">All dates</option>
              <option value="thisweek">This week (last 7 days)</option>
              <option value="last2weeks">Last 2 weeks</option>
              <option value="older">Older than 2 weeks</option>
            </select>
          </Stack>

          {/* Label filter */}
          <Stack gap={3}>
            <Text size="small" style={{ fontSize: 10, fontWeight: 600, color: P.grey, letterSpacing: "0.06em", textTransform: "uppercase" as const }}>Label</Text>
            <select
              value={filterLabel}
              onChange={(e: { target: { value: string } }) => setFilterLabel(e.target.value)}
              style={selectBase}
            >
              <option value="">All labels</option>
              {ALL_LABELS.map(l => (
                <option key={l} value={l}>{l}</option>
              ))}
            </select>
          </Stack>

          {/* Sprint filter */}
          <Stack gap={3}>
            <Text size="small" style={{ fontSize: 10, fontWeight: 600, color: P.grey, letterSpacing: "0.06em", textTransform: "uppercase" as const }}>Sprint</Text>
            <select
              value={filterSprint}
              onChange={(e: { target: { value: string } }) => setFilterSprint(e.target.value)}
              style={selectBase}
            >
              <option value="">All sprints</option>
              {ALL_SPRINTS.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </Stack>
        </Grid>

        {/* Active filter chips + results count */}
        <Row gap={8} align="center" wrap>
          <Text size="small" style={{ fontSize: 11, color: P.grey }}>
            {filtered.length === ISSUES.length
              ? `${ISSUES.length} issues`
              : `${filtered.length} of ${ISSUES.length} issues`}
          </Text>
          {search && (
            <span style={{
              display: "inline-flex", alignItems: "center", gap: 4,
              padding: "2px 8px", borderRadius: 20,
              background: P.lavender, color: P.charcoal, fontSize: 11,
            }}>
              "{search}"
              <button onClick={() => setSearch("")} style={{ all: "unset", cursor: "pointer", lineHeight: 1, fontSize: 10, color: P.grey }}>✕</button>
            </span>
          )}
          {filterLabel && (
            <span style={{
              display: "inline-flex", alignItems: "center", gap: 4,
              padding: "2px 8px", borderRadius: 20,
              background: P.mint, color: P.charcoal, fontSize: 11,
            }}>
              {filterLabel}
              <button onClick={() => setFilterLabel("")} style={{ all: "unset", cursor: "pointer", lineHeight: 1, fontSize: 10, color: P.grey }}>✕</button>
            </span>
          )}
          {filterSprint && (
            <span style={{
              display: "inline-flex", alignItems: "center", gap: 4,
              padding: "2px 8px", borderRadius: 20,
              background: P.blush, color: P.charcoal, fontSize: 11,
            }}>
              {filterSprint}
              <button onClick={() => setFilterSprint("")} style={{ all: "unset", cursor: "pointer", lineHeight: 1, fontSize: 10, color: P.grey }}>✕</button>
            </span>
          )}
          {filterDate !== "all" && (
            <span style={{
              display: "inline-flex", alignItems: "center", gap: 4,
              padding: "2px 8px", borderRadius: 20,
              background: "#f59e0b22", color: "#b45309", fontSize: 11,
            }}>
              {filterDate === "thisweek" ? "This week" : filterDate === "last2weeks" ? "Last 2 weeks" : "Older"}
              <button onClick={() => setFilterDate("all")} style={{ all: "unset", cursor: "pointer", lineHeight: 1, fontSize: 10, color: "#b45309" }}>✕</button>
            </span>
          )}
          {hasFilter && (
            <button
              onClick={clearAll}
              style={{ all: "unset", cursor: "pointer", fontSize: 11, color: P.grey, textDecoration: "underline" }}
            >
              Clear all
            </button>
          )}
        </Row>
      </Stack>

      {/* View tabs */}
      <Row gap={8}>
        <Pill active={view === "cycle"}  onClick={() => setView("cycle")}>Cycle time</Pill>
        <Pill active={view === "board"}  onClick={() => setView("board")}>Board</Pill>
        <Pill active={view === "sprint"} onClick={() => setView("sprint")}>Sprint table</Pill>
      </Row>

      {/* Empty state */}
      {filtered.length === 0 && (
        <div style={{
          textAlign: "center", padding: "48px 24px",
          borderRadius: 10, border: `1.5px dashed ${P.blushBorder}`,
          background: P.blush,
        }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>🔍</div>
          <Text weight="semibold" style={{ color: P.charcoal }}>No issues match your filters</Text>
          <Text size="small" tone="secondary" style={{ marginTop: 4 }}>
            Try adjusting the search or clearing a filter.
          </Text>
          <button
            onClick={clearAll}
            style={{
              all: "unset", cursor: "pointer", marginTop: 12,
              padding: "6px 14px", borderRadius: 6,
              background: P.lavender, color: P.charcoal,
              fontSize: 12, fontWeight: 500,
            }}
          >
            Clear all filters
          </button>
        </div>
      )}

      {/* ── CYCLE TIME VIEW ── */}
      {view === "cycle" && filtered.length > 0 && (
        <Stack gap={20}>

          {filteredOpen.length > 0 && (
            <>
              <button
                onClick={() => setShowOpenIssues(!showOpenIssues)}
                style={{
                  all: "unset", cursor: "pointer", display: "flex", alignItems: "center",
                  gap: 8, width: "100%",
                }}
              >
                <span style={{
                  fontSize: 11, display: "inline-block",
                  transform: showOpenIssues ? "rotate(90deg)" : "rotate(0deg)",
                  transition: "transform 0.15s",
                }}>▶</span>
                <Stack gap={4} style={{ flex: 1 }}>
                  <H2>Open issues ({filteredOpen.length})</H2>
                  <Text tone="secondary" size="small">In Progress first, then Ready for Review / Todo. Time elapsed since assignment — no PR merged yet.</Text>
                </Stack>
              </button>

              {showOpenIssues && filteredOpen.map(issue => {
                const isInProg = issue.status === "In Progress";
                return (
                  <div key={issue.number}>
                    <Card style={{
                      borderLeft: `3px solid ${isInProg ? "#f59e0b" : P.lavenderDeep}`,
                      background: (isInProg ? "#f59e0b" : P.lavender) + "22",
                    }}>
                      <CardHeader trailing={
                        <Row gap={8} align="center">
                          <Text size="small" tone="secondary" style={{ fontSize: 11 }}>
                            Open: <Text as="span" weight="semibold">
                              {fmtHours((Date.now() - new Date(issue.assignedAt).getTime()) / 3600000)}
                            </Text>
                          </Text>
                          <StatusBadge status={issue.status} />
                        </Row>
                      }>
                        #{issue.number}
                      </CardHeader>
                      <CardBody>
                        <Stack gap={10}>
                          <Text size="small" weight="medium">{issue.title}</Text>
                          <TimelineBar issue={issue} />
                          <Grid columns={2} gap={8}>
                            <Stack gap={2}>
                              <Text size="small" tone="tertiary" style={{ fontSize: 10 }}>ASSIGNED</Text>
                              <Text size="small">{fmtDate(issue.assignedAt)}</Text>
                              <Text size="small" tone="tertiary" style={{ fontSize: 10 }}>{fmtTime(issue.assignedAt)}</Text>
                            </Stack>
                            <Stack gap={2}>
                              <Text size="small" tone="tertiary" style={{ fontSize: 10 }}>STATUS</Text>
                              <StatusBadge status={issue.status} />
                            </Stack>
                          </Grid>
                          <Row gap={4} wrap>
                            {issue.labels.map(l => <span key={l}><LabelChip name={l} /></span>)}
                          </Row>
                        </Stack>
                      </CardBody>
                    </Card>
                  </div>
                );
              })}
            </>
          )}

          {filteredDone.length > 0 && (
            <>
              <button
                onClick={() => setShowDoneIssues(!showDoneIssues)}
                style={{
                  all: "unset", cursor: "pointer", display: "flex", alignItems: "center",
                  gap: 8, width: "100%",
                }}
              >
                <span style={{
                  fontSize: 11, display: "inline-block",
                  transform: showDoneIssues ? "rotate(90deg)" : "rotate(0deg)",
                  transition: "transform 0.15s",
                }}>▶</span>
                <Stack gap={4} style={{ flex: 1 }}>
                  <H2>Completed issues ({filteredDone.length})</H2>
                  <Text tone="secondary" size="small">Time from project "Todo" entry to resolution. Bar segments: <span style={{ color: "#f59e0b", fontWeight: 600 }}>■ In Progress</span> · <span style={{ fontWeight: 600 }}>■ Review / Closed</span>. Amber tick marks the Todo → In Progress transition.</Text>
                </Stack>
              </button>

              {showDoneIssues && filteredDone.map(issue => {
                const isOpen = expanded.includes(issue.number);
                const s = issue.prSummary;
                return (
                  <div key={issue.number}>
                    <Card style={{ borderLeft: `3px solid ${issue.status === "Closed" ? P.grey : P.mintDeep}`, background: (issue.status === "Closed" ? P.grey : P.mintDeep) + "22" }}>
                      <CardHeader trailing={
                        <Row gap={8} align="center">
                          <Text size="small" tone="secondary" style={{ fontSize: 11 }}>
                            Total: <Text as="span" weight="semibold">{fmtHours(issue.cycleHours!)}</Text>
                          </Text>
                          <StatusBadge status={issue.status} />
                        </Row>
                      }>
                        #{issue.number}
                      </CardHeader>
                      <CardBody>
                        <Stack gap={10}>
                          <Text size="small" weight="medium">{issue.title}</Text>
                          <TimelineBar issue={issue} />
                          <Grid columns={3} gap={8}>
                            <Stack gap={2}>
                              <Text size="small" tone="tertiary" style={{ fontSize: 10 }}>ASSIGNED</Text>
                              <Text size="small">{fmtDate(issue.assignedAt)}</Text>
                              <Text size="small" tone="tertiary" style={{ fontSize: 10 }}>{fmtTime(issue.assignedAt)}</Text>
                            </Stack>
                            <Stack gap={2}>
                              <Text size="small" tone="tertiary" style={{ fontSize: 10 }}>PR OPENED</Text>
                              <Text size="small">{issue.prCreatedAt ? fmtDate(issue.prCreatedAt) : "—"}</Text>
                              {issue.prCreatedAt && (
                                <Text size="small" tone="tertiary" style={{ fontSize: 10 }}>
                                  {fmtTime(issue.prCreatedAt)} · after {fmtHours((new Date(issue.prCreatedAt).getTime() - new Date(issue.assignedAt).getTime()) / 3600000)} of work
                                </Text>
                              )}
                            </Stack>
                            <Stack gap={2}>
                              <Text size="small" tone="tertiary" style={{ fontSize: 10 }}>MERGED</Text>
                              <Text size="small">{issue.mergedAt ? fmtDate(issue.mergedAt) : "—"}</Text>
                              {issue.mergedAt && issue.prCreatedAt && (
                                <Text size="small" tone="tertiary" style={{ fontSize: 10 }}>
                                  {fmtTime(issue.mergedAt)} · PR open for {fmtHours(issue.prOpenHours!)}
                                </Text>
                              )}
                            </Stack>
                          </Grid>
                          {issue.prNumber && (
                            <Row gap={6} align="center">
                              <Text size="small" tone="tertiary" style={{ fontSize: 10 }}>PR</Text>
                              <Link href={issue.prUrl!} style={{ fontSize: 11 }}>#{issue.prNumber} {issue.prTitle}</Link>
                            </Row>
                          )}
                          <Row gap={4} wrap>
                            {issue.labels.map(l => <span key={l}><LabelChip name={l} /></span>)}
                          </Row>

                          {/* PR / Closing Summary dropdown */}
                          {s && (
                            <Stack gap={0}>
                              <button
                                onClick={() => toggleExpanded(issue.number)}
                                style={{
                                  all: "unset", cursor: "pointer",
                                  display: "flex", alignItems: "center", gap: 6,
                                  padding: "6px 10px",
                                  borderRadius: isOpen ? "6px 6px 0 0" : 6,
                                  background: isOpen ? P.lavender : P.blush,
                                  border: `1px solid ${P.blushBorder}`,
                                  fontSize: 11, color: P.charcoal, fontWeight: 500,
                                  userSelect: "none",
                                }}
                              >
                                <span style={{ fontSize: 10, display: "inline-block", transform: isOpen ? "rotate(90deg)" : "rotate(0deg)" }}>▶</span>
                                {issue.status === "Closed" ? "Closing Summary" : "PR Solution Summary"}
                                <span style={{ marginLeft: "auto", fontSize: 10, color: P.grey, fontWeight: 400 }}>
                                  {isOpen ? "hide" : "show"}
                                </span>
                              </button>
                              {isOpen && (
                                <div style={{
                                  padding: "12px 14px",
                                  border: `1px solid ${P.blushBorder}`,
                                  borderTop: "none",
                                  borderRadius: "0 0 6px 6px",
                                  background: P.blush,
                                }}>
                                  <Stack gap={10}>
                                    <Row gap={6} align="center">
                                      <span style={{
                                        fontSize: 9, padding: "2px 6px", borderRadius: 3,
                                        background: s.prType.startsWith("Closed") ? "#e0e0e0" : P.lavender,
                                        color: s.prType.startsWith("Closed") ? "#666" : P.charcoal,
                                        fontWeight: 500,
                                      }}>
                                        {s.prType}
                                      </span>
                                    </Row>
                                    <Stack gap={4}>
                                      <Text size="small" style={{ fontSize: 10, fontWeight: 600, color: P.grey, letterSpacing: "0.05em", textTransform: "uppercase" as const }}>Problem</Text>
                                      <Text size="small" style={{ fontSize: 12, lineHeight: 1.5, color: P.charcoal }}>{s.problem}</Text>
                                    </Stack>
                                    <Stack gap={4}>
                                      <Text size="small" style={{ fontSize: 10, fontWeight: 600, color: P.grey, letterSpacing: "0.05em", textTransform: "uppercase" as const }}>Solution</Text>
                                      <Text size="small" style={{ fontSize: 12, lineHeight: 1.5, color: P.charcoal }}>{s.solution}</Text>
                                    </Stack>
                                    <Stack gap={6}>
                                      <Text size="small" style={{ fontSize: 10, fontWeight: 600, color: P.grey, letterSpacing: "0.05em", textTransform: "uppercase" as const }}>Key Changes</Text>
                                      <Stack gap={4}>
                                        {s.keyChanges.map((change, i) => (
                                          <div key={i} style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
                                            <span style={{ color: P.mintDeep, fontWeight: 700, fontSize: 12, lineHeight: 1.5, flexShrink: 0 }}>✓</span>
                                            <Text size="small" style={{ fontSize: 12, lineHeight: 1.5, color: P.charcoal }}>{change}</Text>
                                          </div>
                                        ))}
                                      </Stack>
                                    </Stack>
                                  </Stack>
                                </div>
                              )}
                            </Stack>
                          )}
                        </Stack>
                      </CardBody>
                    </Card>
                  </div>
                );
              })}
            </>
          )}
        </Stack>
      )}

      {/* ── BOARD VIEW ── */}
      {view === "board" && filtered.length > 0 && (
        <Grid columns={5} gap={12} align="start">
          {STATUS_ORDER.map(status => {
            const items = byStatusF(status);
            return (
              <div key={status}>
                <Stack gap={8}>
                  <Row gap={6} align="center">
                    <Text weight="semibold" size="small" style={{
                      color: status === "In Progress" ? "#b45309" : P.charcoal,
                    }}>
                      {status}
                    </Text>
                    <span style={{
                      fontSize: 10, borderRadius: "50%", width: 18, height: 18,
                      display: "flex", alignItems: "center", justifyContent: "center",
                      background: theme.fill.secondary, color: theme.text.tertiary,
                    }}>
                      {items.length}
                    </span>
                  </Row>
                  <div style={{
                    height: 2, borderRadius: 1,
                    background: status === "Done" ? P.mintDeep : status === "Closed" ? P.grey : status === "In Progress" ? "#f59e0b" : P.lavenderDeep,
                  }} />
                  {items.length === 0
                    ? <Text size="small" tone="quaternary" italic>—</Text>
                    : items.map(issue => (
                        <div key={issue.number} style={{
                          borderRadius: 5, padding: "10px 12px",
                          border: `1px solid ${P.blushBorder}`,
                          background: issue.status === "Done" ? P.mint + "55" : issue.status === "Closed" ? "#f0f0f0" : issue.status === "In Progress" ? "#f59e0b11" : P.lavender + "55",
                          opacity: (issue.status === "Done" || issue.status === "Closed") ? 0.8 : 1,
                        }}>
                          <Stack gap={5}>
                            <Row gap={6} align="center">
                              <Link href={issue.url} style={{ fontSize: 11, fontFamily: "monospace", color: theme.text.tertiary }}>
                                #{issue.number}
                              </Link>
                              <Spacer />
                              {issue.cycleHours && (
                                <Text size="small" tone="tertiary" style={{ fontSize: 10 }}>{fmtHours(issue.cycleHours)}</Text>
                              )}
                            </Row>
                            <Text size="small" weight="medium" style={{
                              lineHeight: 1.4,
                              textDecoration: (issue.status === "Done" || issue.status === "Closed") ? "line-through" : "none",
                              color: (issue.status === "Done" || issue.status === "Closed") ? theme.text.tertiary : theme.text.primary,
                            }}>
                              {issue.title}
                            </Text>
                            {issue.prNumber && (
                              <Link href={issue.prUrl!} style={{ fontSize: 10 }}>PR #{issue.prNumber}</Link>
                            )}
                          </Stack>
                        </div>
                      ))
                  }
                </Stack>
              </div>
            );
          })}
        </Grid>
      )}

      {/* ── SPRINT TABLE ── */}
      {view === "sprint" && filtered.length > 0 && (
        <Stack gap={12}>
          <H2>Sprint table — {filtered.length} issue{filtered.length !== 1 ? "s" : ""}</H2>
          <Table
            striped stickyHeader
            headers={["#", "Title", "Status", "Labels", "Assigned", "PR Opened", "Merged", "Cycle Time", "PR Review"]}
            columnAlign={["left", "left", "left", "left", "left", "left", "left", "right", "right"]}
            rowTone={filtered.map(i =>
              i.status === "Done" ? "success" as const :
              i.status === "Closed" ? "neutral" as const :
              i.status === "In Progress" ? "info" as const : "neutral" as const
            )}
            rows={filtered.map(i => [
              <Link href={i.url} style={{ fontFamily: "monospace", fontSize: 11 }}>#{i.number}</Link>,
              <Text size="small" truncate style={{ maxWidth: 220 }}>{i.title}</Text>,
              <StatusBadge status={i.status} />,
              <Row gap={3} wrap>
                {i.labels.filter(l => l !== "good first issue").map(l => (
                  <span key={l}><LabelChip name={l} /></span>
                ))}
              </Row>,
              <Text size="small" tone="secondary">{fmtDate(i.assignedAt)}</Text>,
              <Text size="small" tone="secondary">{i.prCreatedAt ? fmtDate(i.prCreatedAt) : "—"}</Text>,
              <Text size="small" tone="secondary">{i.mergedAt ? fmtDate(i.mergedAt) : "—"}</Text>,
              i.cycleHours
                ? <Text size="small" weight="semibold">{fmtHours(i.cycleHours)}</Text>
                : <Text size="small" tone="tertiary">
                    {fmtHours((Date.now() - new Date(i.assignedAt).getTime()) / 3600000)}+
                  </Text>,
              i.prOpenHours
                ? <Text size="small">{fmtHours(i.prOpenHours)}</Text>
                : <Text size="small" tone="tertiary">—</Text>,
            ])}
          />
        </Stack>
      )}

    </Stack>
  );
}
