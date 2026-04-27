#!/usr/bin/env node
/**
 * Kener bootstrap script — runs INSIDE the Kener container.
 *
 * Idempotent: applies Mandari branding, replaces the default demo monitors
 * (earth + kener) with real Mandari monitors, and creates an API key the
 * marketing website uses to pull live status data.
 *
 * The plain-text API key is printed to STDOUT on the line:
 *     KENER_API_TOKEN=<token>
 *
 * Re-running the script after a key already exists will NOT print a new
 * token (we cannot recover the plaintext from the hash). To rotate the key,
 * delete it first via UI or DB.
 *
 * Usage:
 *     docker exec -e KENER_SECRET_KEY=$KENER_SECRET_KEY \
 *         marketing-website-kener node /tmp/kener-bootstrap.mjs
 */

import Database from "better-sqlite3";
import crypto from "crypto";

// ─────────────────────────── config ───────────────────────────

const DB_PATH = "/app/database/kener.sqlite.db";
const API_KEY_NAME = "mandari-marketing-bootstrap";

const SITE_BRANDING = {
    title: "Mandari Status",
    siteName: "Mandari",
    siteURL: process.env.ORIGIN || "http://localhost:6501",
    home: "/",
    hero: {
        title: "System-Status",
        subtitle: "Live-Verfügbarkeit aller Mandari-Dienste — Insight, Work, Verwaltungs-RIS und OParl-Ingestor.",
    },
    metaTags: [
        { key: "description", value: "Live-Status der Mandari-Plattform für kommunalpolitische Transparenz." },
        { key: "og:description", value: "Live-Status der Mandari-Plattform für kommunalpolitische Transparenz." },
        { key: "og:title", value: "Mandari Status" },
        { key: "og:type", value: "website" },
        { key: "og:site_name", value: "Mandari" },
    ],
    nav: [
        { name: "Mandari", url: "https://mandari.de", iconURL: "" },
        { name: "Dokumentation", url: "https://github.com/mandariOSS/mandari", iconURL: "" },
        { name: "Login", url: "/account/signin", iconURL: "" },
    ],
    footerHTML:
        '<div class="container relative mt-4 max-w-[800px]">' +
        '<div class="block items-center gap-4 px-8 md:flex-row md:gap-2 md:px-0 mx-auto">' +
        '<p class="text-center text-xs leading-loose text-muted-foreground">' +
        "Mandari · Open Source unter " +
        '<a href="https://www.gnu.org/licenses/agpl-3.0.html" target="_blank" rel="noopener" ' +
        'class="font-medium underline underline-offset-4 hover:text-accent-foreground">AGPL-3.0</a> · ' +
        '<a href="https://mandari.de/impressum/" target="_blank" rel="noopener" ' +
        'class="font-medium underline underline-offset-4 hover:text-accent-foreground">Impressum</a> · ' +
        '<a href="https://mandari.de/datenschutz/" target="_blank" rel="noopener" ' +
        'class="font-medium underline underline-offset-4 hover:text-accent-foreground">Datenschutz</a>' +
        "<br/>Status-Page powered by " +
        '<a href="https://github.com/rajnandan1/kener" target="_blank" rel="noopener" ' +
        'class="font-medium underline underline-offset-4 hover:text-accent-foreground">Kener</a>.' +
        "</p></div></div>",
    colors: {
        UP: "#10b981", // emerald-500
        DOWN: "#ef4444", // red-500
        DEGRADED: "#f59e0b", // amber-500
        MAINTENANCE: "#6366f1", // indigo-500 (Mandari primary)
        ACCENT: "#f4f4f5",
        ACCENT_FOREGROUND: "#4f46e5", // indigo-600
    },
    colorsDark: {
        UP: "#10b981",
        DOWN: "#ef4444",
        DEGRADED: "#f59e0b",
        MAINTENANCE: "#6366f1",
        ACCENT: "#27272a",
        ACCENT_FOREGROUND: "#818cf8", // indigo-400 (better contrast on dark)
    },
    categories: [
        { name: "Mandari Plattform", description: "Öffentliche Portale und Anwendungen", isHidden: false },
        { name: "Daten & Quellen", description: "OParl-Ingestor und externe Datenquellen", isHidden: false },
    ],
    showSiteStatus: "YES",
    barStyle: "PARTIAL",
    barRoundness: "ROUNDED",
    summaryStyle: "CURRENT",
    kenerTheme: "system",
    themeToggle: "YES",
    tzToggle: "YES",
};

const PAGE_BRANDING = {
    page_title: "Mandari Status",
    page_header: "System-Status",
    page_subheader:
        "Live-Verfügbarkeit aller Mandari-Dienste. Vorfälle und geplante Wartungsfenster werden hier dokumentiert.",
    page_logo: "",
};

// Real endpoints we can monitor right now.
const REAL_MONITORS = [
    {
        tag: "marketing-website",
        name: "Marketing-Website",
        description: "mandari.de — die öffentliche Marketing- und Dokumentationsseite.",
        category_name: "Mandari Plattform",
        url: "http://website:8001/health/",
        position: 0,
    },
    {
        tag: "oparl-muenster",
        name: "OParl-Quelle: Münster",
        description: "Beispiel einer öffentlichen OParl-1.1-Schnittstelle, die Mandari aggregiert.",
        category_name: "Daten & Quellen",
        url: "https://oparl.stadt-muenster.de/system",
        position: 4,
    },
];

// Demo monitors for services that aren't running yet — point at a public
// always-200 endpoint so they show as UP, with a description that explains
// "Demo until launch". This gives the page a realistic look + and-feel.
const DEMO_MONITORS = [
    {
        tag: "mandari-insight",
        name: "Mandari Insight",
        description: "Öffentliches Bürger-Portal mit Suche, Karten und KI-Zusammenfassungen. (Demo bis Launch)",
        category_name: "Mandari Plattform",
        url: "https://httpbin.org/status/200",
        position: 1,
    },
    {
        tag: "mandari-work",
        name: "Mandari Work",
        description: "Geschützter Arbeitsbereich für Fraktionen und politische Organisationen. (Demo bis Launch)",
        category_name: "Mandari Plattform",
        url: "https://httpbin.org/status/200",
        position: 2,
    },
    {
        tag: "mandari-session",
        name: "Mandari Verwaltungs-RIS",
        description: "Sitzungs- und Antragsverwaltung für Kommunen. (Demo bis Launch)",
        category_name: "Mandari Plattform",
        url: "https://httpbin.org/status/200",
        position: 3,
    },
    {
        tag: "oparl-ingestor",
        name: "OParl-Ingestor & API",
        description: "Datensynchronisation aus OParl-Quellen und öffentliche API. (Demo bis Launch)",
        category_name: "Daten & Quellen",
        url: "https://httpbin.org/status/200",
        position: 5,
    },
];

const ALL_MANDARI_MONITORS = [...REAL_MONITORS, ...DEMO_MONITORS];
const OBSOLETE_MONITOR_TAGS = ["earth", "kener"];

// ─────────────────────────── helpers ───────────────────────────

function maskString(str) {
    return "*".repeat(Math.max(0, str.length - 4)) + str.slice(-4);
}

function hashApiKey(plaintext) {
    const secret = process.env.KENER_SECRET_KEY || "DUMMY_SECRET";
    return crypto.createHmac("sha256", secret).update(plaintext).digest("hex");
}

/**
 * UPSERT semantics for site_data: there is no UNIQUE on `key` so we do
 * UPDATE-then-INSERT manually.
 */
function setSiteData(db, key, value, dataType) {
    const valueText = dataType === "object" ? JSON.stringify(value) : String(value);
    const updated = db
        .prepare("UPDATE site_data SET value = ?, data_type = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?")
        .run(valueText, dataType, key);
    if (updated.changes === 0) {
        db.prepare("INSERT INTO site_data (key, value, data_type) VALUES (?, ?, ?)").run(key, valueText, dataType);
    }
}

function buildHttpTypeData(url) {
    return JSON.stringify({
        url,
        method: "GET",
        headers: [],
        body: "",
        timeout: 10000,
        eval:
            "(async function (statusCode, responseTime, responseRaw, modules) {\n" +
            "    let s = Math.floor(statusCode / 100);\n" +
            "    if (statusCode === 429 || (s >= 2 && s <= 3)) {\n" +
            "        return { status: 'UP', latency: responseTime };\n" +
            "    }\n" +
            "    return { status: 'DOWN', latency: responseTime };\n" +
            "})",
        allowSelfSignedCert: false,
    });
}

const MONITOR_SETTINGS_DEFAULT = JSON.stringify({
    uptime_formula_numerator: "up + maintenance",
    uptime_formula_denominator: "up + maintenance + down + degraded",
});

// ─────────────────────────── main ───────────────────────────

function main() {
    const db = new Database(DB_PATH);
    db.pragma("foreign_keys = ON");

    let createdToken = null;

    db.transaction(() => {
        // 1. Site branding
        for (const [key, value] of Object.entries(SITE_BRANDING)) {
            const dataType = typeof value === "object" ? "object" : "string";
            setSiteData(db, key, value, dataType);
        }
        console.error(`✓ Site branding applied (${Object.keys(SITE_BRANDING).length} keys)`);

        // 2. Page (id=1, the default page)
        const pageRow = db.prepare("SELECT id FROM pages WHERE id = 1").get();
        if (pageRow) {
            db.prepare(
                "UPDATE pages SET page_title = ?, page_header = ?, page_subheader = ?, page_logo = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1",
            ).run(
                PAGE_BRANDING.page_title,
                PAGE_BRANDING.page_header,
                PAGE_BRANDING.page_subheader,
                PAGE_BRANDING.page_logo,
            );
            console.error("✓ Page 1 updated to Mandari branding");
        }

        // 3. Remove obsolete demo monitors (and their page assignments)
        for (const tag of OBSOLETE_MONITOR_TAGS) {
            db.prepare("DELETE FROM pages_monitors WHERE monitor_tag = ?").run(tag);
            const result = db.prepare("DELETE FROM monitors WHERE tag = ?").run(tag);
            if (result.changes > 0) {
                console.error(`✓ Removed obsolete monitor: ${tag}`);
            }
        }

        // 4. Insert/update Mandari monitors
        const insertMonitor = db.prepare(
            "INSERT INTO monitors (tag, name, description, image, cron, default_status, status, category_name, " +
                "monitor_type, type_data, day_degraded_minimum_count, day_down_minimum_count, " +
                "include_degraded_in_downtime, is_hidden, monitor_settings_json) " +
                "VALUES (?, ?, ?, '', '* * * * *', 'UP', 'ACTIVE', ?, 'API', ?, 1, 1, 'NO', 'NO', ?)",
        );
        const updateMonitor = db.prepare(
            "UPDATE monitors SET name = ?, description = ?, category_name = ?, type_data = ?, " +
                "monitor_settings_json = ?, updated_at = CURRENT_TIMESTAMP WHERE tag = ?",
        );

        for (const m of ALL_MANDARI_MONITORS) {
            const exists = db.prepare("SELECT id FROM monitors WHERE tag = ?").get(m.tag);
            const typeData = buildHttpTypeData(m.url);
            if (exists) {
                updateMonitor.run(
                    m.name,
                    m.description,
                    m.category_name,
                    typeData,
                    MONITOR_SETTINGS_DEFAULT,
                    m.tag,
                );
                console.error(`↻ Monitor updated: ${m.tag}`);
            } else {
                insertMonitor.run(m.tag, m.name, m.description, m.category_name, typeData, MONITOR_SETTINGS_DEFAULT);
                console.error(`+ Monitor created: ${m.tag}`);
            }
        }

        // 5. pages_monitors associations (idempotent on PK page_id+monitor_tag)
        const upsertAssoc = db.prepare(
            "INSERT INTO pages_monitors (page_id, monitor_tag, position, monitor_settings_json) " +
                "VALUES (1, ?, ?, '') " +
                "ON CONFLICT(page_id, monitor_tag) DO UPDATE SET position = excluded.position, updated_at = CURRENT_TIMESTAMP",
        );
        for (const m of ALL_MANDARI_MONITORS) {
            upsertAssoc.run(m.tag, m.position);
        }
        console.error(`✓ ${ALL_MANDARI_MONITORS.length} monitors assigned to default page`);

        // 6. API key — create only if a Mandari key doesn't already exist
        const existing = db.prepare("SELECT id, masked_key FROM api_keys WHERE name = ?").get(API_KEY_NAME);
        if (existing) {
            console.error(
                `↪ API key already exists (id=${existing.id}, masked=${existing.masked_key}). ` +
                    "Plaintext is unrecoverable — delete via UI to rotate.",
            );
        } else {
            const plaintext = crypto.randomBytes(32).toString("hex");
            const hashed = hashApiKey(plaintext);
            const masked = maskString(plaintext);
            db.prepare("INSERT INTO api_keys (name, hashed_key, masked_key) VALUES (?, ?, ?)").run(
                API_KEY_NAME,
                hashed,
                masked,
            );
            createdToken = plaintext;
            console.error(`+ API key created: ${API_KEY_NAME} (masked=${masked})`);
        }
    })();

    db.close();

    // Emit token on stdout (only line on stdout — easy to parse)
    if (createdToken) {
        process.stdout.write(`KENER_API_TOKEN=${createdToken}\n`);
    } else {
        process.stdout.write("KENER_API_TOKEN=__EXISTS__\n");
    }
}

try {
    main();
} catch (err) {
    console.error("Bootstrap failed:", err);
    process.exit(1);
}
