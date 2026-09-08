import { useMemo } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, AreaChart, Area, BarChart, Bar, Legend,
} from "recharts";

// ---------------------------------------------------------------------
// Dit component leest normaal gesproken `dashboard_data.json`, het
// bestand dat geo_tracker.py exporteert (`python geo_tracker.py report`).
// Hieronder staat voorbeelddata in exact dezelfde vorm, zodat je kunt
// zien hoe ruwe metingen zich vertalen naar het overzicht dat een klant
// te zien krijgt. Vervang MOCK_WEEKLY / MOCK_MODELS / MOCK_LOG door een
// fetch() of import van je eigen dashboard_data.json.
// ---------------------------------------------------------------------

const BRAND = "Noordzee Boekhoud";
const COMPETITORS = ["Ledger & Co", "CijferPartners"];

const MOCK_WEEKLY = [
  { week: "Wk 1", brand: 8, comp1: 34, comp2: 21 },
  { week: "Wk 2", brand: 11, comp1: 31, comp2: 19 },
  { week: "Wk 3", brand: 14, comp1: 33, comp2: 22 },
  { week: "Wk 4", brand: 19, comp1: 30, comp2: 20 },
  { week: "Wk 5", brand: 27, comp1: 29, comp2: 18 },
  { week: "Wk 6", brand: 33, comp1: 28, comp2: 17 },
  { week: "Wk 7", brand: 38, comp1: 27, comp2: 19 },
  { week: "Wk 8", brand: 44, comp1: 26, comp2: 16 },
  { week: "Wk 9", brand: 49, comp1: 25, comp2: 15 },
  { week: "Wk 10", brand: 55, comp1: 24, comp2: 14 },
];

const MOCK_MODELS = [
  { model: "ChatGPT", share: 58 },
  { model: "Perplexity", share: 41 },
  { model: "Gemini", share: 62 },
];

const MOCK_LOG = [
  { ts: "2 sep, 09:14", model: "ChatGPT", prompt: "beste boekhoudsoftware zzp Rotterdam", hit: true, domain: "noordzeeboekhoud.nl" },
  { ts: "2 sep, 09:14", model: "Perplexity", prompt: "boekhouder kiezen als freelancer NL", hit: false, domain: "ledgerenco.nl" },
  { ts: "1 sep, 22:03", model: "Gemini", prompt: "goedkope boekhouding kleine ondernemer", hit: true, domain: "noordzeeboekhoud.nl" },
  { ts: "1 sep, 22:03", model: "ChatGPT", prompt: "boekhoudpakket vergelijken 2026", hit: true, domain: "noordzeeboekhoud.nl" },
  { ts: "31 aug, 15:40", model: "Perplexity", prompt: "beste online boekhouder Nederland", hit: false, domain: "cijferpartners.nl" },
  { ts: "31 aug, 08:52", model: "Gemini", prompt: "zzp boekhouding uitbesteden kosten", hit: true, domain: "noordzeeboekhoud.nl" },
];

const COLORS = {
  brand: "#fbbf24",
  comp1: "#2dd4bf",
  comp2: "#64748b",
  hit: "#fbbf24",
  miss: "#fb7185",
};

function Stat({ label, value, sub }) {
  return (
    <div>
      <div className="font-serif text-5xl text-slate-100 tabular-nums">{value}</div>
      <div className="mt-1 text-sm text-slate-400">{label}</div>
      {sub && <div className="mt-0.5 text-sm text-amber-400">{sub}</div>}
    </div>
  );
}

export default function GeoDashboard() {
  const latest = MOCK_WEEKLY[MOCK_WEEKLY.length - 1];
  const first = MOCK_WEEKLY[0];
  const delta = latest.brand - first.brand;
  const avgCompetitor = Math.round((latest.comp1 + latest.comp2) / 2);

  const overallShare = useMemo(() => {
    const total = MOCK_LOG.length;
    const hits = MOCK_LOG.filter((r) => r.hit).length;
    return Math.round((hits / total) * 100);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 px-6 py-10 md:px-12">
      <div className="mx-auto max-w-4xl">

        {/* Header */}
        <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-slate-800 pb-6">
          <div>
            <h1 className="font-serif text-2xl text-slate-100">{BRAND}</h1>
            <p className="mt-1 text-sm text-slate-400">AI-zichtbaarheidsrapport — gemeten over ChatGPT, Perplexity &amp; Gemini</p>
          </div>
          <p className="font-mono text-xs text-slate-500">26 jun – 2 sep 2026</p>
        </div>

        {/* Hero: kerncijfer + sparkline */}
        <div className="grid grid-cols-1 gap-8 border-b border-slate-800 py-8 md:grid-cols-[auto,1fr]">
          <Stat
            label="citatie-aandeel, laatste meetweek"
            value={`${latest.brand}%`}
            sub={`+${delta}pp sinds start van de opdracht`}
          />
          <div className="h-24 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={MOCK_WEEKLY} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
                <defs>
                  <linearGradient id="sparkFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={COLORS.brand} stopOpacity={0.35} />
                    <stop offset="100%" stopColor={COLORS.brand} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <Area
                  type="monotone" dataKey="brand" stroke={COLORS.brand}
                  strokeWidth={2} fill="url(#sparkFill)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Trend: merk vs concurrenten */}
        <div className="border-b border-slate-800 py-8">
          <h2 className="font-serif text-lg text-slate-200">Aandeel van stem, per week</h2>
          <p className="mt-1 text-sm text-slate-400">
            Percentage van de vaste promptset waarin elk merk genoemd of geciteerd wordt.
          </p>
          <div className="mt-6 h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={MOCK_WEEKLY} margin={{ top: 4, right: 8, bottom: 0, left: -16 }}>
                <CartesianGrid stroke="#1e293b" vertical={false} />
                <XAxis dataKey="week" stroke="#64748b" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis stroke="#64748b" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} unit="%" />
                <Tooltip
                  contentStyle={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: 4, fontSize: 13 }}
                  labelStyle={{ color: "#e2e8f0" }}
                />
                <Legend wrapperStyle={{ fontSize: 13, color: "#94a3b8" }} iconType="line" />
                <Line type="monotone" dataKey="brand" name={BRAND} stroke={COLORS.brand} strokeWidth={2.5} dot={false} />
                <Line type="monotone" dataKey="comp1" name={COMPETITORS[0]} stroke={COLORS.comp1} strokeWidth={1.5} dot={false} />
                <Line type="monotone" dataKey="comp2" name={COMPETITORS[1]} stroke={COLORS.comp2} strokeWidth={1.5} dot={false} strokeDasharray="4 3" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Twee kolommen: per model + recent log */}
        <div className="grid grid-cols-1 gap-10 py-8 md:grid-cols-2">
          <div>
            <h2 className="font-serif text-lg text-slate-200">Per model</h2>
            <p className="mt-1 text-sm text-slate-400">Citatie-aandeel deze meetperiode, uitgesplitst.</p>
            <div className="mt-6 h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={MOCK_MODELS} layout="vertical" margin={{ top: 0, right: 16, bottom: 0, left: 0 }}>
                  <XAxis type="number" domain={[0, 100]} hide />
                  <YAxis
                    type="category" dataKey="model" width={80}
                    stroke="#94a3b8" tick={{ fontSize: 13 }} axisLine={false} tickLine={false}
                  />
                  <Tooltip
                    contentStyle={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: 4, fontSize: 13 }}
                    cursor={{ fill: "#1e293b", opacity: 0.4 }}
                  />
                  <Bar dataKey="share" fill={COLORS.brand} radius={[0, 3, 3, 0]} barSize={18} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="mt-4 text-sm text-slate-400">
              Gemiddeld concurrent-aandeel: <span className="text-slate-200">{avgCompetitor}%</span> —
              {" "}{BRAND} staat er dus {latest.brand > avgCompetitor ? "voor" : "nog achter"}.
            </p>
          </div>

          <div>
            <h2 className="font-serif text-lg text-slate-200">Recente metingen</h2>
            <p className="mt-1 text-sm text-slate-400">Live doorloop van de vaste promptset ({overallShare}% hit rate).</p>
            <div className="mt-6 divide-y divide-slate-800 border-t border-slate-800">
              {MOCK_LOG.map((row, i) => (
                <div key={i} className="flex items-start gap-3 py-3">
                  <span
                    className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full"
                    style={{ background: row.hit ? COLORS.hit : COLORS.miss }}
                  />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm text-slate-200">{row.prompt}</p>
                    <p className="mt-0.5 font-mono text-xs text-slate-500">
                      {row.model} · {row.ts} · {row.hit ? row.domain : `geciteerd: ${row.domain}`}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <p className="border-t border-slate-800 pt-6 font-mono text-xs text-slate-600">
          Gegenereerd uit dashboard_data.json · python geo_tracker.py report
        </p>
      </div>
    </div>
  );
}
