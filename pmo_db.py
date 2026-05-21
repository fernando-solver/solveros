"""
PMO Database - Sistema de memoria estruturada para projetos.

Banco SQLite com FTS5 para rastreamento de sessoes, atividades, pendencias e skills.
Uso: importado pelo Claude Code via Bash (python -c "from pmo_db import ...")
ou diretamente em scripts.
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pmo.db")


def get_conn():
    """Retorna conexao SQLite com WAL mode e foreign keys."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Cria schema completo (idempotente)."""
    conn = get_conn()
    c = conn.cursor()

    # -- Sessoes de trabalho com o Claude --
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT DEFAULT (datetime('now','localtime')),
            ended_at TEXT,
            summary TEXT,
            status TEXT DEFAULT 'active'  -- active | completed | lost
        )
    """)

    # -- Atividades (granular, tipado) --
    c.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER REFERENCES sessions(id),
            date TEXT NOT NULL,
            project TEXT NOT NULL,
            type TEXT NOT NULL,
            summary TEXT NOT NULL,
            details TEXT,
            files_changed TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    # -- Pendencias --
    c.execute("""
        CREATE TABLE IF NOT EXISTS pending (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            resolved INTEGER DEFAULT 0,
            resolved_at TEXT
        )
    """)

    # -- Projetos (espelho do GLOSSARIO) --
    c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folder TEXT UNIQUE NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Ativo',
            empresa TEXT,
            departamento TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            last_activity TEXT
        )
    """)

    # Migracao idempotente: garante empresa/departamento em projects (DBs criados antes da v0.7)
    _proj_cols = [r[1] for r in c.execute("PRAGMA table_info(projects)").fetchall()]
    if 'empresa' not in _proj_cols:
        c.execute("ALTER TABLE projects ADD COLUMN empresa TEXT")
    if 'departamento' not in _proj_cols:
        c.execute("ALTER TABLE projects ADD COLUMN departamento TEXT")

    # -- Objetivos estrategicos --
    c.execute("""
        CREATE TABLE IF NOT EXISTS objectives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            horizon TEXT NOT NULL,          -- trimestral | semestral | anual
            status TEXT DEFAULT 'active',   -- active | achieved | abandoned | paused
            target_date TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            achieved_at TEXT
        )
    """)

    # -- Vinculo projeto <-> objetivo --
    c.execute("""
        CREATE TABLE IF NOT EXISTS project_objectives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_folder TEXT NOT NULL,
            objective_id INTEGER NOT NULL REFERENCES objectives(id),
            contribution TEXT,
            UNIQUE(project_folder, objective_id)
        )
    """)

    # -- Skills (memoria procedural auto-melhoravel) --
    c.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            trigger TEXT,                   -- quando usar (texto livre)
            file_path TEXT,                 -- caminho do .md relativo ao workspace
            version INTEGER DEFAULT 1,
            status TEXT DEFAULT 'active',   -- active | deprecated | retired
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime')),
            uses_count INTEGER DEFAULT 0
        )
    """)

    # -- Usos de skills (log de cada vez que uma skill e usada) --
    c.execute("""
        CREATE TABLE IF NOT EXISTS skill_uses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id INTEGER NOT NULL REFERENCES skills(id),
            session_id INTEGER REFERENCES sessions(id),
            project TEXT,
            date TEXT NOT NULL,
            outcome TEXT,                   -- sucesso | falha | parcial
            improvement_noted TEXT,         -- sugestao de melhoria observada
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    # -- Shares (log de compartilhamentos de projeto) --
    c.execute("""
        CREATE TABLE IF NOT EXISTS shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT NOT NULL,
            zip_path TEXT NOT NULL,
            destinatario TEXT,
            generated_at TEXT DEFAULT (datetime('now','localtime')),
            size_bytes INTEGER,
            files_count INTEGER,
            notes TEXT
        )
    """)

    # -- Clientes (v0.5 — empresas cadastradas no SolverOS) --
    c.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            segmento TEXT,
            ticket_medio REAL,
            mrr REAL,
            status TEXT DEFAULT 'ativo',
            identidade_visual_json TEXT,
            contato_json TEXT,
            agencia_atual_custo_brl REAL,
            criado_em TEXT DEFAULT (datetime('now','localtime')),
            atualizado_em TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    # -- Cliente objetivos (v0.5 — meta financeira/operacional do cliente) --
    c.execute("""
        CREATE TABLE IF NOT EXISTS cliente_objetivos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
            tipo TEXT NOT NULL,
            descricao TEXT,
            valor_alvo REAL,
            valor_atual REAL,
            horizonte TEXT,
            prazo TEXT,
            status TEXT DEFAULT 'ativo',
            criado_em TEXT DEFAULT (datetime('now','localtime')),
            atingido_em TEXT
        )
    """)

    # -- Metricas diarias (v0.5 — schema metrica-centrico, fonte rastreavel) --
    c.execute("""
        CREATE TABLE IF NOT EXISTS metricas_diarias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
            data TEXT NOT NULL,
            canal TEXT NOT NULL,
            campanha TEXT,
            investimento_brl REAL DEFAULT 0,
            impressoes INTEGER DEFAULT 0,
            clicks INTEGER DEFAULT 0,
            conversoes INTEGER DEFAULT 0,
            receita_brl REAL DEFAULT 0,
            fonte_arquivo TEXT,
            importado_em TEXT DEFAULT (datetime('now','localtime')),
            UNIQUE(cliente_id, data, canal, campanha)
        )
    """)

    # -- Cliente index (v0.5 — ponteiro canonico tipo INDEX.md) --
    c.execute("""
        CREATE TABLE IF NOT EXISTS cliente_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
            tipo_artefato TEXT NOT NULL,
            caminho_canonico TEXT NOT NULL,
            hash_conteudo TEXT,
            metadados_json TEXT,
            atualizado_em TEXT DEFAULT (datetime('now','localtime')),
            UNIQUE(cliente_id, tipo_artefato)
        )
    """)

    # -- Artefatos arquivados (v0.5 — Camada C, archive seguro) --
    c.execute("""
        CREATE TABLE IF NOT EXISTS artefatos_arquivados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER REFERENCES clientes(id) ON DELETE SET NULL,
            caminho_original TEXT NOT NULL,
            caminho_archive TEXT NOT NULL,
            motivo TEXT,
            hash_conteudo TEXT,
            arquivado_em TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    # -- Auditoria de entropia (v0.5 — Camada B, deteccao semanal) --
    c.execute("""
        CREATE TABLE IF NOT EXISTS auditoria_entropia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER REFERENCES clientes(id) ON DELETE CASCADE,
            data TEXT NOT NULL,
            tipo_problema TEXT NOT NULL,
            severidade TEXT DEFAULT 'media',
            descricao TEXT,
            caminho_envolvido TEXT,
            resolvido INTEGER DEFAULT 0,
            resolvido_em TEXT
        )
    """)

    # -- DB snapshots (v0.5 — recuperacao via snapshot semanal) --
    c.execute("""
        CREATE TABLE IF NOT EXISTS db_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_path TEXT NOT NULL,
            sha256 TEXT,
            size_bytes INTEGER,
            criado_em TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    # -- FTS5 para busca full-text em atividades --
    c.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS activities_fts USING fts5(
            project, type, summary, details,
            content=activities,
            content_rowid=id
        )
    """)

    # -- FTS5 para busca full-text em skills --
    c.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS skills_fts USING fts5(
            name, description, trigger,
            content=skills,
            content_rowid=id
        )
    """)

    # -- Triggers para manter FTS sincronizado --
    c.execute("""
        CREATE TRIGGER IF NOT EXISTS activities_ai AFTER INSERT ON activities BEGIN
            INSERT INTO activities_fts(rowid, project, type, summary, details)
            VALUES (new.id, new.project, new.type, new.summary, new.details);
        END
    """)
    c.execute("""
        CREATE TRIGGER IF NOT EXISTS activities_ad AFTER DELETE ON activities BEGIN
            INSERT INTO activities_fts(activities_fts, rowid, project, type, summary, details)
            VALUES ('delete', old.id, old.project, old.type, old.summary, old.details);
        END
    """)
    c.execute("""
        CREATE TRIGGER IF NOT EXISTS activities_au AFTER UPDATE ON activities BEGIN
            INSERT INTO activities_fts(activities_fts, rowid, project, type, summary, details)
            VALUES ('delete', old.id, old.project, old.type, old.summary, old.details);
            INSERT INTO activities_fts(rowid, project, type, summary, details)
            VALUES (new.id, new.project, new.type, new.summary, new.details);
        END
    """)

    # -- Triggers FTS para skills --
    c.execute("""
        CREATE TRIGGER IF NOT EXISTS skills_ai AFTER INSERT ON skills BEGIN
            INSERT INTO skills_fts(rowid, name, description, trigger)
            VALUES (new.id, new.name, new.description, new.trigger);
        END
    """)
    c.execute("""
        CREATE TRIGGER IF NOT EXISTS skills_ad AFTER DELETE ON skills BEGIN
            INSERT INTO skills_fts(skills_fts, rowid, name, description, trigger)
            VALUES ('delete', old.id, old.name, old.description, old.trigger);
        END
    """)
    c.execute("""
        CREATE TRIGGER IF NOT EXISTS skills_au AFTER UPDATE ON skills BEGIN
            INSERT INTO skills_fts(skills_fts, rowid, name, description, trigger)
            VALUES ('delete', old.id, old.name, old.description, old.trigger);
            INSERT INTO skills_fts(rowid, name, description, trigger)
            VALUES (new.id, new.name, new.description, new.trigger);
        END
    """)

    # -- Indices --
    c.execute("CREATE INDEX IF NOT EXISTS idx_activities_date ON activities(date DESC)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_activities_project ON activities(project)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(type)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_activities_session ON activities(session_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_pending_project ON pending(project)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_pending_resolved ON pending(resolved)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_skills_status ON skills(status)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_skill_uses_skill ON skill_uses(skill_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_shares_project ON shares(project)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_shares_generated ON shares(generated_at DESC)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_clientes_status ON clientes(status)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_cliente_objetivos_cliente ON cliente_objetivos(cliente_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_cliente_objetivos_status ON cliente_objetivos(status)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_metricas_cliente_data ON metricas_diarias(cliente_id, data DESC)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_metricas_canal ON metricas_diarias(canal)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_cliente_index_cliente ON cliente_index(cliente_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_artefatos_cliente ON artefatos_arquivados(cliente_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_auditoria_cliente ON auditoria_entropia(cliente_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_auditoria_resolvido ON auditoria_entropia(resolvido, severidade)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_criado ON db_snapshots(criado_em DESC)")

    conn.commit()
    conn.close()
    return "[OK] Schema criado/verificado"


# ============================================================
# SESSOES
# ============================================================

def session_start(summary=None):
    """Inicia nova sessao. Retorna session_id."""
    conn = get_conn()
    c = conn.execute("INSERT INTO sessions (summary) VALUES (?)", (summary,))
    sid = c.lastrowid
    conn.commit()
    conn.close()
    return sid


def session_end(session_id, summary=None):
    """Encerra sessao."""
    conn = get_conn()
    conn.execute(
        "UPDATE sessions SET ended_at=datetime('now','localtime'), status='completed', summary=COALESCE(?,summary) WHERE id=?",
        (summary, session_id)
    )
    conn.commit()
    conn.close()


def session_last():
    """Retorna ultima sessao."""
    conn = get_conn()
    row = conn.execute("SELECT * FROM sessions ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return dict(row) if row else None


def session_context(n=3):
    """Retorna as ultimas N sessoes com suas atividades."""
    conn = get_conn()
    sessions = conn.execute(
        "SELECT * FROM sessions ORDER BY id DESC LIMIT ?", (n,)
    ).fetchall()
    result = []
    for s in sessions:
        s_dict = dict(s)
        acts = conn.execute(
            "SELECT date, project, type, summary FROM activities WHERE session_id=? ORDER BY id",
            (s['id'],)
        ).fetchall()
        s_dict['activities'] = [dict(a) for a in acts]
        result.append(s_dict)
    conn.close()
    return result


# ============================================================
# ATIVIDADES
# ============================================================

def log_activity(date, project, type_, summary, details=None, files_changed=None, session_id=None):
    """Registra uma atividade."""
    conn = get_conn()
    files_json = json.dumps(files_changed) if files_changed else None
    conn.execute(
        "INSERT INTO activities (session_id, date, project, type, summary, details, files_changed) VALUES (?,?,?,?,?,?,?)",
        (session_id, date, project, type_, summary, details, files_json)
    )
    conn.execute(
        "UPDATE projects SET last_activity=? WHERE folder LIKE ?",
        (date, f"%{project}%")
    )
    conn.commit()
    conn.close()


def query_activities(where="1=1", params=(), limit=50):
    """Query generica em activities."""
    conn = get_conn()
    rows = conn.execute(
        f"SELECT * FROM activities WHERE {where} ORDER BY date DESC, id DESC LIMIT ?",
        params + (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_activities(text, limit=20):
    """Busca full-text em atividades."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT a.* FROM activities a
        JOIN activities_fts f ON a.id = f.rowid
        WHERE activities_fts MATCH ?
        ORDER BY a.date DESC LIMIT ?
    """, (text, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def activities_by_project(project, limit=50):
    return query_activities("project LIKE ?", (f"%{project}%",), limit)


def activities_by_date_range(start, end, limit=100):
    return query_activities("date >= ? AND date <= ?", (start, end), limit)


def activities_by_type(type_, limit=50):
    return query_activities("type = ?", (type_,), limit)


def project_stats():
    """Estatisticas por projeto."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT project, COUNT(*) as total_activities, COUNT(DISTINCT date) as days_worked,
               MAX(date) as last_activity, GROUP_CONCAT(DISTINCT type) as types
        FROM activities GROUP BY project ORDER BY last_activity DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def inactive_projects(days=30):
    """Projetos sem atividade em N dias."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT project, MAX(date) as last_activity,
               CAST(julianday('now') - julianday(MAX(date)) AS INTEGER) as days_inactive
        FROM activities GROUP BY project
        HAVING MAX(date) < date('now', ? || ' days') ORDER BY last_activity
    """, (f"-{days}",)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# PENDENCIAS
# ============================================================

def add_pending(project, description):
    """Adiciona pendencia."""
    conn = get_conn()
    c = conn.execute("INSERT INTO pending (project, description) VALUES (?,?)", (project, description))
    pid = c.lastrowid
    conn.commit()
    conn.close()
    return pid


def resolve_pending(pending_id):
    """Marca pendencia como resolvida."""
    conn = get_conn()
    conn.execute(
        "UPDATE pending SET resolved=1, resolved_at=datetime('now','localtime') WHERE id=?",
        (pending_id,)
    )
    conn.commit()
    conn.close()


def list_pending(project=None, resolved=False):
    """Lista pendencias abertas (ou todas)."""
    conn = get_conn()
    if project:
        rows = conn.execute(
            "SELECT * FROM pending WHERE project LIKE ? AND resolved=? ORDER BY created_at DESC",
            (f"%{project}%", int(resolved))
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM pending WHERE resolved=? ORDER BY created_at DESC",
            (int(resolved),)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# PROJETOS
# ============================================================

def upsert_project(folder, description=None, status=None, empresa=None, departamento=None):
    """Insere ou atualiza projeto. empresa/departamento sao campos queryaveis."""
    conn = get_conn()
    existing = conn.execute("SELECT * FROM projects WHERE folder=?", (folder,)).fetchone()
    if existing:
        updates, params = [], []
        if description:
            updates.append("description=?"); params.append(description)
        if status:
            updates.append("status=?"); params.append(status)
        if empresa:
            updates.append("empresa=?"); params.append(empresa)
        if departamento:
            updates.append("departamento=?"); params.append(departamento)
        if updates:
            params.append(folder)
            conn.execute(f"UPDATE projects SET {','.join(updates)} WHERE folder=?", params)
    else:
        conn.execute(
            "INSERT INTO projects (folder, description, status, empresa, departamento) VALUES (?,?,?,?,?)",
            (folder, description, status or 'Ativo', empresa, departamento)
        )
    conn.commit()
    conn.close()


# ============================================================
# OBJETIVOS ESTRATEGICOS
# ============================================================

def add_objective(title, description, horizon, target_date=None):
    """Cria objetivo estrategico. Retorna id."""
    conn = get_conn()
    c = conn.execute(
        "INSERT INTO objectives (title, description, horizon, target_date) VALUES (?,?,?,?)",
        (title, description, horizon, target_date)
    )
    oid = c.lastrowid
    conn.commit()
    conn.close()
    return oid


def update_objective(objective_id, title=None, description=None, horizon=None, target_date=None, status=None):
    """Atualiza campos de um objetivo."""
    conn = get_conn()
    updates, params = [], []
    for field, val in [('title', title), ('description', description), ('horizon', horizon),
                       ('target_date', target_date), ('status', status)]:
        if val is not None:
            updates.append(f"{field}=?"); params.append(val)
    if updates:
        params.append(objective_id)
        conn.execute(f"UPDATE objectives SET {','.join(updates)} WHERE id=?", params)
    conn.commit()
    conn.close()


def link_project_objective(project_folder, objective_id, contribution=None):
    """Vincula projeto a um objetivo."""
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO project_objectives (project_folder, objective_id, contribution) VALUES (?,?,?)",
        (project_folder, objective_id, contribution)
    )
    conn.commit()
    conn.close()


def list_objectives(status='active'):
    """Lista objetivos por status."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM objectives WHERE status=? ORDER BY target_date", (status,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def objective_progress(objective_id):
    """Retorna projetos vinculados e suas atividades recentes."""
    conn = get_conn()
    obj = conn.execute("SELECT * FROM objectives WHERE id=?", (objective_id,)).fetchone()
    if not obj:
        conn.close()
        return None
    result = dict(obj)
    projects = conn.execute("""
        SELECT po.project_folder, po.contribution, p.status, p.description
        FROM project_objectives po LEFT JOIN projects p ON p.folder = po.project_folder
        WHERE po.objective_id = ?
    """, (objective_id,)).fetchall()
    result['projects'] = []
    for proj in projects:
        p = dict(proj)
        last = conn.execute("""
            SELECT date, type, summary FROM activities
            WHERE project = ? ORDER BY date DESC, id DESC LIMIT 3
        """, (proj['project_folder'],)).fetchall()
        p['recent_activities'] = [dict(a) for a in last]
        days = conn.execute(
            "SELECT COUNT(DISTINCT date) as days FROM activities WHERE project = ?",
            (proj['project_folder'],)
        ).fetchone()
        p['days_worked'] = days['days']
        result['projects'].append(p)
    conn.close()
    return result


def orphan_projects():
    """Projetos ativos sem vinculo a nenhum objetivo."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT p.folder, p.description, p.status FROM projects p
        WHERE p.status IN ('Ativo', 'Em andamento')
        AND p.folder NOT IN (SELECT project_folder FROM project_objectives)
        ORDER BY p.folder
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def objective_dashboard():
    """Visao geral dos objetivos com progresso."""
    conn = get_conn()
    objs = conn.execute("SELECT * FROM objectives WHERE status='active' ORDER BY id").fetchall()
    result = []
    for obj in objs:
        o = dict(obj)
        projs = conn.execute("""
            SELECT po.project_folder, p.status FROM project_objectives po
            LEFT JOIN projects p ON p.folder = po.project_folder WHERE po.objective_id = ?
        """, (obj['id'],)).fetchall()
        o['total_projects'] = len(projs)
        o['active_projects'] = sum(1 for p in projs if p['status'] in ('Ativo', 'Em andamento'))
        acts = conn.execute("""
            SELECT COUNT(*) as n FROM activities a JOIN project_objectives po ON a.project = po.project_folder
            WHERE po.objective_id = ? AND a.date >= date('now', 'start of month')
        """, (obj['id'],)).fetchone()
        o['activities_this_month'] = acts['n']
        result.append(o)
    orphans = conn.execute("""
        SELECT COUNT(*) as n FROM projects WHERE status IN ('Ativo', 'Em andamento')
        AND folder NOT IN (SELECT project_folder FROM project_objectives)
    """).fetchone()
    conn.close()
    return {'objectives': result, 'orphan_projects': orphans['n']}


# ============================================================
# SKILLS (memoria procedural auto-melhoravel)
# ============================================================

def register_skill(name, description, trigger, file_path=None):
    """
    Registra nova skill. Retorna id.

    Args:
        name: identificador unico da skill (ex: 'skill_01_extrair-palestra')
        description: o que a skill faz, em 1 frase
        trigger: texto livre descrevendo quando invocar
        file_path: caminho do .md da skill (opcional)
    """
    conn = get_conn()
    c = conn.execute(
        "INSERT INTO skills (name, description, trigger, file_path) VALUES (?,?,?,?)",
        (name, description, trigger, file_path)
    )
    sid = c.lastrowid
    conn.commit()
    conn.close()
    return sid


def update_skill(skill_id, description=None, trigger=None, file_path=None, bump_version=False, status=None):
    """Atualiza skill. bump_version=True incrementa a versao."""
    conn = get_conn()
    updates, params = [], []
    for field, val in [('description', description), ('trigger', trigger),
                       ('file_path', file_path), ('status', status)]:
        if val is not None:
            updates.append(f"{field}=?"); params.append(val)
    if bump_version:
        updates.append("version=version+1")
    updates.append("updated_at=datetime('now','localtime')")
    params.append(skill_id)
    conn.execute(f"UPDATE skills SET {','.join(updates)} WHERE id=?", params)
    conn.commit()
    conn.close()


def log_skill_use(skill_id, project, date=None, session_id=None, outcome='sucesso', improvement_noted=None):
    """
    Registra uso de uma skill e incrementa o contador.

    Args:
        skill_id: id da skill usada
        project: pasta do projeto onde foi usada
        date: YYYY-MM-DD (default: hoje)
        session_id: id da sessao atual (opcional)
        outcome: 'sucesso' | 'falha' | 'parcial'
        improvement_noted: sugestao de melhoria observada no uso (opcional)
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    conn = get_conn()
    conn.execute(
        "INSERT INTO skill_uses (skill_id, session_id, project, date, outcome, improvement_noted) VALUES (?,?,?,?,?,?)",
        (skill_id, session_id, project, date, outcome, improvement_noted)
    )
    conn.execute("UPDATE skills SET uses_count = uses_count + 1 WHERE id=?", (skill_id,))
    conn.commit()
    conn.close()


def list_skills(status='active'):
    """Lista skills por status."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM skills WHERE status=? ORDER BY uses_count DESC, name",
        (status,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def skill_by_name(name):
    """Busca skill pelo nome. Retorna dict ou None."""
    conn = get_conn()
    row = conn.execute("SELECT * FROM skills WHERE name=?", (name,)).fetchone()
    conn.close()
    return dict(row) if row else None


def find_skill_local(query, limit=5):
    """
    Descobre skills locais relevantes para uma descricao de tarefa.

    Ranking:
      - rank FTS5 (BM25) * 2.0
      - (1.0 + uses_count * 0.1) * 0.5 quando uses_count > 0
      - 0.3 se usada nos ultimos 30 dias (recencia)

    Args:
        query: descricao em linguagem natural da tarefa
        limit: max skills a retornar (default 5)

    Returns:
        Lista de dicts com id, name, description, trigger, uses_count, version,
        fts_score, recent_uses. Ordenado por score desc.

    Se query vazia, retorna top skills por uses_count.
    """
    conn = get_conn()
    if not query or not query.strip():
        rows = conn.execute("""
            SELECT id, name, description, trigger, uses_count, version,
                   0 as fts_score, 0 as recent_uses
            FROM skills WHERE status='active'
            ORDER BY uses_count DESC LIMIT ?
        """, (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    # Sanitiza para FTS5 — remove caracteres com significado especial
    safe = query.replace('"', '').replace('(', '').replace(')', '').replace('*', '').strip()
    if not safe:
        conn.close()
        return []
    # Para descoberta ampla, usamos OR entre tokens (recall > precisao)
    tokens = [t for t in safe.split() if t]
    fts_query = ' OR '.join(tokens) if tokens else safe
    try:
        rows = conn.execute("""
            SELECT s.id, s.name, s.description, s.trigger, s.uses_count, s.version,
                   -skills_fts.rank as fts_score,
                   (SELECT COUNT(*) FROM skill_uses su
                    WHERE su.skill_id = s.id
                    AND su.date > date('now', '-30 days')) as recent_uses
            FROM skills_fts JOIN skills s ON s.id = skills_fts.rowid
            WHERE skills_fts MATCH ? AND s.status='active'
            ORDER BY (
              -skills_fts.rank * 2.0
              + (CASE WHEN s.uses_count > 0 THEN
                  (1.0 + s.uses_count * 0.1) * 0.5 ELSE 0 END)
              + (CASE WHEN (SELECT COUNT(*) FROM skill_uses su2
                            WHERE su2.skill_id = s.id
                            AND su2.date > date('now', '-30 days')) > 0
                 THEN 0.3 ELSE 0 END)
            ) DESC
            LIMIT ?
        """, (fts_query, limit)).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        # Se FTS falhar (query malformada), fallback para LIKE
        safe_like = f"%{safe}%"
        rows = conn.execute("""
            SELECT id, name, description, trigger, uses_count, version,
                   0 as fts_score, 0 as recent_uses
            FROM skills WHERE status='active'
            AND (name LIKE ? OR description LIKE ? OR trigger LIKE ?)
            ORDER BY uses_count DESC LIMIT ?
        """, (safe_like, safe_like, safe_like, limit)).fetchall()
        conn.close()
        return [dict(r) for r in rows]


def fts_rebuild_skills():
    """Rebuild do indice FTS5 de skills (usar se ficar dessincronizado)."""
    conn = get_conn()
    conn.execute("INSERT INTO skills_fts(skills_fts) VALUES('rebuild')")
    conn.commit()
    conn.close()


def skill_improvements_pending():
    """
    Lista skills com sugestoes de melhoria observadas mas ainda nao aplicadas.
    Util para revisao periodica pelo PMO.
    """
    conn = get_conn()
    rows = conn.execute("""
        SELECT s.name, s.version, su.date, su.project, su.improvement_noted
        FROM skill_uses su JOIN skills s ON su.skill_id = s.id
        WHERE su.improvement_noted IS NOT NULL
        ORDER BY su.date DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# UTILIDADES
# ============================================================

def raw_query(sql, params=()):
    """
    Executa SQL arbitrario. Suporta SELECT (retorna rows) e
    UPDATE/INSERT/DELETE (aplica commit e retorna lista vazia).
    """
    conn = get_conn()
    cur = conn.execute(sql, params)
    # Detecta se e query de leitura ou mutacao
    sql_upper = sql.strip().upper()
    is_read = sql_upper.startswith(('SELECT', 'WITH', 'PRAGMA', 'EXPLAIN'))
    if is_read:
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    else:
        conn.commit()
        conn.close()
        return []


def db_stats():
    """Resumo do banco."""
    conn = get_conn()
    stats = {}
    for table in ['sessions', 'activities', 'pending', 'projects',
                  'objectives', 'project_objectives', 'skills', 'skill_uses',
                  'shares']:
        row = conn.execute(f"SELECT COUNT(*) as n FROM {table}").fetchone()
        stats[table] = row['n']
    conn.close()
    return stats


# ============================================================
# SHARES (log de compartilhamentos de projeto)
# ============================================================

def add_share(project, zip_path, destinatario=None, size_bytes=None, files_count=None, notes=None):
    """Registra um share de projeto. Retorna id."""
    conn = get_conn()
    c = conn.execute(
        "INSERT INTO shares (project, zip_path, destinatario, size_bytes, files_count, notes) VALUES (?,?,?,?,?,?)",
        (project, zip_path, destinatario, size_bytes, files_count, notes)
    )
    sid = c.lastrowid
    conn.commit()
    conn.close()
    return sid


def shares_log(project=None, limit=50):
    """Lista shares (do projeto informado ou todos)."""
    conn = get_conn()
    if project:
        rows = conn.execute(
            "SELECT * FROM shares WHERE project LIKE ? ORDER BY generated_at DESC LIMIT ?",
            (f"%{project}%", limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM shares ORDER BY generated_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# CLIENTES (v0.5 — empresas cadastradas no SolverOS)
# ============================================================

def cliente_create(slug, nome, segmento=None, ticket_medio=None, mrr=None,
                   identidade_visual_json=None, contato_json=None,
                   agencia_atual_custo_brl=None):
    """Cria cliente. slug deve ser unico (kebab-case). Retorna id."""
    conn = get_conn()
    iv = json.dumps(identidade_visual_json) if isinstance(identidade_visual_json, dict) else identidade_visual_json
    ct = json.dumps(contato_json) if isinstance(contato_json, dict) else contato_json
    c = conn.execute(
        """INSERT INTO clientes
           (slug, nome, segmento, ticket_medio, mrr,
            identidade_visual_json, contato_json, agencia_atual_custo_brl)
           VALUES (?,?,?,?,?,?,?,?)""",
        (slug, nome, segmento, ticket_medio, mrr, iv, ct, agencia_atual_custo_brl)
    )
    cid = c.lastrowid
    conn.commit()
    conn.close()
    return cid


def cliente_get(slug_or_id):
    """Busca cliente por slug (str) ou id (int). Retorna dict ou None."""
    conn = get_conn()
    if isinstance(slug_or_id, int):
        row = conn.execute("SELECT * FROM clientes WHERE id=?", (slug_or_id,)).fetchone()
    else:
        row = conn.execute("SELECT * FROM clientes WHERE slug=?", (slug_or_id,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    for k in ("identidade_visual_json", "contato_json"):
        if d.get(k):
            try:
                d[k] = json.loads(d[k])
            except (ValueError, TypeError):
                pass
    return d


def cliente_update(slug, **fields):
    """Atualiza campos do cliente. Aceita kwargs para qualquer coluna editavel.
    Sempre atualiza atualizado_em. Retorna True se afetou linha."""
    editaveis = {
        "nome", "segmento", "ticket_medio", "mrr", "status",
        "identidade_visual_json", "contato_json", "agencia_atual_custo_brl"
    }
    sets = []
    vals = []
    for k, v in fields.items():
        if k not in editaveis:
            continue
        if k in ("identidade_visual_json", "contato_json") and isinstance(v, dict):
            v = json.dumps(v)
        sets.append(f"{k}=?")
        vals.append(v)
    if not sets:
        return False
    sets.append("atualizado_em=datetime('now','localtime')")
    vals.append(slug)
    conn = get_conn()
    cur = conn.execute(f"UPDATE clientes SET {', '.join(sets)} WHERE slug=?", vals)
    conn.commit()
    affected = cur.rowcount
    conn.close()
    return affected > 0


def cliente_list(status=None):
    """Lista clientes. Filtro opcional por status (ativo/pausado/encerrado)."""
    conn = get_conn()
    if status:
        rows = conn.execute(
            "SELECT * FROM clientes WHERE status=? ORDER BY nome", (status,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM clientes ORDER BY nome").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# CLIENTE OBJETIVOS (v0.5 - meta financeira/operacional)
# ============================================================

def objetivo_add(cliente_id, tipo, valor_alvo=None, descricao=None,
                 horizonte=None, prazo=None, valor_atual=None):
    """Adiciona objetivo a um cliente. tipo: faturamento_mensal | roas | cac |
    aov | recompra | ltv | nps. Retorna id."""
    conn = get_conn()
    c = conn.execute(
        """INSERT INTO cliente_objetivos
           (cliente_id, tipo, descricao, valor_alvo, valor_atual, horizonte, prazo)
           VALUES (?,?,?,?,?,?,?)""",
        (cliente_id, tipo, descricao, valor_alvo, valor_atual, horizonte, prazo)
    )
    oid = c.lastrowid
    conn.commit()
    conn.close()
    return oid


def objetivo_update(obj_id, **fields):
    """Atualiza objetivo. Aceita: descricao, valor_alvo, valor_atual, horizonte,
    prazo, status. Se status='atingido', define atingido_em."""
    editaveis = {"descricao", "valor_alvo", "valor_atual", "horizonte", "prazo", "status"}
    sets, vals = [], []
    for k, v in fields.items():
        if k in editaveis:
            sets.append(f"{k}=?")
            vals.append(v)
    if not sets:
        return False
    if fields.get("status") == "atingido":
        sets.append("atingido_em=datetime('now','localtime')")
    vals.append(obj_id)
    conn = get_conn()
    cur = conn.execute(f"UPDATE cliente_objetivos SET {', '.join(sets)} WHERE id=?", vals)
    conn.commit()
    affected = cur.rowcount
    conn.close()
    return affected > 0


def objetivo_progress(cliente_id):
    """Retorna progresso de cada objetivo ativo do cliente: pct = valor_atual/valor_alvo.
    Para tipo CAC menor e melhor: pct invertido."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM cliente_objetivos WHERE cliente_id=? AND status='ativo' ORDER BY tipo",
        (cliente_id,)
    ).fetchall()
    conn.close()
    out = []
    menor_e_melhor = {"cac"}
    for r in rows:
        d = dict(r)
        alvo, atual = d.get("valor_alvo"), d.get("valor_atual")
        if alvo and atual is not None and alvo != 0:
            if d["tipo"] in menor_e_melhor:
                d["pct"] = (alvo / atual) if atual else None
            else:
                d["pct"] = atual / alvo
        else:
            d["pct"] = None
        out.append(d)
    return out


def objetivos_em_risco(threshold_pct=0.5):
    """Lista objetivos ativos com progresso abaixo do threshold (ex: <50% do alvo).
    Retorna join com nome do cliente."""
    conn = get_conn()
    rows = conn.execute(
        """SELECT o.*, c.slug AS cliente_slug, c.nome AS cliente_nome
           FROM cliente_objetivos o
           JOIN clientes c ON c.id = o.cliente_id
           WHERE o.status='ativo'
             AND o.valor_alvo IS NOT NULL AND o.valor_alvo > 0
             AND o.valor_atual IS NOT NULL
             AND (o.valor_atual / o.valor_alvo) < ?
             AND o.tipo NOT IN ('cac')
           ORDER BY (o.valor_atual / o.valor_alvo) ASC""",
        (threshold_pct,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def objetivo_list(cliente_id=None, status="ativo"):
    """Lista objetivos. Filtros opcionais por cliente_id e status."""
    conn = get_conn()
    where, args = [], []
    if cliente_id:
        where.append("cliente_id=?")
        args.append(cliente_id)
    if status:
        where.append("status=?")
        args.append(status)
    sql = "SELECT * FROM cliente_objetivos"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY criado_em DESC"
    rows = conn.execute(sql, args).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# METRICAS DIARIAS (v0.5 - schema metrica-centrico)
# ============================================================

def metrica_log_batch(rows):
    """Insere/atualiza metricas em lote (UPSERT por cliente_id+data+canal+campanha).
    rows: lista de dicts com chaves: cliente_id, data, canal, [campanha,
    investimento_brl, impressoes, clicks, conversoes, receita_brl, fonte_arquivo].
    Retorna numero de linhas afetadas."""
    if not rows:
        return 0
    conn = get_conn()
    affected = 0
    for r in rows:
        conn.execute(
            """INSERT INTO metricas_diarias
               (cliente_id, data, canal, campanha, investimento_brl,
                impressoes, clicks, conversoes, receita_brl, fonte_arquivo)
               VALUES (?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(cliente_id, data, canal, campanha) DO UPDATE SET
                 investimento_brl=excluded.investimento_brl,
                 impressoes=excluded.impressoes,
                 clicks=excluded.clicks,
                 conversoes=excluded.conversoes,
                 receita_brl=excluded.receita_brl,
                 fonte_arquivo=excluded.fonte_arquivo,
                 importado_em=datetime('now','localtime')""",
            (r["cliente_id"], r["data"], r["canal"], r.get("campanha"),
             r.get("investimento_brl", 0), r.get("impressoes", 0),
             r.get("clicks", 0), r.get("conversoes", 0),
             r.get("receita_brl", 0), r.get("fonte_arquivo"))
        )
        affected += 1
    conn.commit()
    conn.close()
    return affected


def metricas_periodo(cliente_id, data_inicio, data_fim, canal=None):
    """Agregado de metricas no periodo. Retorna dict com totais + ROAS/CPA/CTR/CR."""
    conn = get_conn()
    sql = """SELECT
               SUM(investimento_brl) AS investimento,
               SUM(impressoes) AS impressoes,
               SUM(clicks) AS clicks,
               SUM(conversoes) AS conversoes,
               SUM(receita_brl) AS receita
             FROM metricas_diarias
             WHERE cliente_id=? AND data BETWEEN ? AND ?"""
    args = [cliente_id, data_inicio, data_fim]
    if canal:
        sql += " AND canal=?"
        args.append(canal)
    row = conn.execute(sql, args).fetchone()
    conn.close()
    d = dict(row) if row else {}
    inv = d.get("investimento") or 0
    rec = d.get("receita") or 0
    imp = d.get("impressoes") or 0
    clk = d.get("clicks") or 0
    conv = d.get("conversoes") or 0
    d["roas"] = (rec / inv) if inv else None
    d["cpa"] = (inv / conv) if conv else None
    d["ctr"] = (clk / imp) if imp else None
    d["cr"] = (conv / clk) if clk else None
    return d


def metricas_canal_compare(cliente_id, data_inicio, data_fim):
    """Compara performance entre canais no periodo. Retorna lista por canal."""
    conn = get_conn()
    rows = conn.execute(
        """SELECT canal,
                  SUM(investimento_brl) AS investimento,
                  SUM(receita_brl) AS receita,
                  SUM(conversoes) AS conversoes,
                  SUM(clicks) AS clicks
           FROM metricas_diarias
           WHERE cliente_id=? AND data BETWEEN ? AND ?
           GROUP BY canal
           ORDER BY investimento DESC""",
        (cliente_id, data_inicio, data_fim)
    ).fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        inv = d.get("investimento") or 0
        rec = d.get("receita") or 0
        conv = d.get("conversoes") or 0
        d["roas"] = (rec / inv) if inv else None
        d["cpa"] = (inv / conv) if conv else None
        out.append(d)
    return out


# ============================================================
# CLIENTE INDEX (v0.5 - INDEX.md canonico)
# ============================================================

def index_set(cliente_id, tipo_artefato, caminho_canonico,
              hash_conteudo=None, metadados=None):
    """UPSERT do canonico para um tipo de artefato. metadados: dict opcional."""
    md = json.dumps(metadados) if isinstance(metadados, dict) else metadados
    conn = get_conn()
    conn.execute(
        """INSERT INTO cliente_index
           (cliente_id, tipo_artefato, caminho_canonico, hash_conteudo, metadados_json)
           VALUES (?,?,?,?,?)
           ON CONFLICT(cliente_id, tipo_artefato) DO UPDATE SET
             caminho_canonico=excluded.caminho_canonico,
             hash_conteudo=excluded.hash_conteudo,
             metadados_json=excluded.metadados_json,
             atualizado_em=datetime('now','localtime')""",
        (cliente_id, tipo_artefato, caminho_canonico, hash_conteudo, md)
    )
    conn.commit()
    conn.close()


def index_get(cliente_id, tipo_artefato):
    """Recupera caminho canonico para um tipo. Retorna dict ou None."""
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM cliente_index WHERE cliente_id=? AND tipo_artefato=?",
        (cliente_id, tipo_artefato)
    ).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    if d.get("metadados_json"):
        try:
            d["metadados_json"] = json.loads(d["metadados_json"])
        except (ValueError, TypeError):
            pass
    return d


def index_resolve_canonical(cliente_id):
    """Retorna {tipo_artefato: caminho_canonico} para todos os canonicos do cliente.
    Base pra geracao do INDEX.md."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT tipo_artefato, caminho_canonico, atualizado_em FROM cliente_index WHERE cliente_id=? ORDER BY tipo_artefato",
        (cliente_id,)
    ).fetchall()
    conn.close()
    return {r["tipo_artefato"]: {"caminho": r["caminho_canonico"], "atualizado_em": r["atualizado_em"]} for r in rows}


# ============================================================
# ARTEFATOS ARQUIVADOS (v0.5 - Camada C, archive seguro)
# ============================================================

def arquivar(caminho_original, caminho_archive, cliente_id=None,
             motivo=None, hash_conteudo=None):
    """Registra arquivamento de um artefato. Nao move arquivo — registra evento.
    motivo: duplicata | versao_obsoleta | sem_referencia | manual."""
    conn = get_conn()
    c = conn.execute(
        """INSERT INTO artefatos_arquivados
           (cliente_id, caminho_original, caminho_archive, motivo, hash_conteudo)
           VALUES (?,?,?,?,?)""",
        (cliente_id, caminho_original, caminho_archive, motivo, hash_conteudo)
    )
    aid = c.lastrowid
    conn.commit()
    conn.close()
    return aid


def arquivados_por_cliente(cliente_id, limit=100):
    """Lista artefatos arquivados de um cliente, mais recentes primeiro."""
    conn = get_conn()
    rows = conn.execute(
        """SELECT * FROM artefatos_arquivados
           WHERE cliente_id=?
           ORDER BY arquivado_em DESC
           LIMIT ?""",
        (cliente_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# AUDITORIA DE ENTROPIA (v0.5 - Camada B, deteccao)
# ============================================================

def auditoria_register(cliente_id, tipo_problema, descricao=None,
                       caminho_envolvido=None, severidade="media",
                       data=None):
    """Registra um problema detectado pela auditoria semanal. tipo_problema:
    duplicata_hash | cadeia_versao | orfao | sem_referencia | sem_canonico |
    inativo | secret_detectado. Retorna id."""
    if data is None:
        data = datetime.now().strftime("%Y-%m-%d")
    conn = get_conn()
    c = conn.execute(
        """INSERT INTO auditoria_entropia
           (cliente_id, data, tipo_problema, severidade, descricao, caminho_envolvido)
           VALUES (?,?,?,?,?,?)""",
        (cliente_id, data, tipo_problema, severidade, descricao, caminho_envolvido)
    )
    aid = c.lastrowid
    conn.commit()
    conn.close()
    return aid


def auditoria_open_issues(cliente_id=None, severidade=None):
    """Lista problemas de entropia nao resolvidos."""
    conn = get_conn()
    where, args = ["resolvido=0"], []
    if cliente_id:
        where.append("cliente_id=?")
        args.append(cliente_id)
    if severidade:
        where.append("severidade=?")
        args.append(severidade)
    sql = ("SELECT * FROM auditoria_entropia WHERE " + " AND ".join(where) +
           " ORDER BY data DESC, severidade DESC")
    rows = conn.execute(sql, args).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# DB SNAPSHOTS (v0.5 - recuperacao via snapshot)
# ============================================================

def snapshot_db(target_dir=None):
    """Cria snapshot do pmo.db em _backups/. Registra em db_snapshots.
    Retorna dict com path, sha256, size, id."""
    import shutil
    import hashlib
    if target_dir is None:
        target_dir = os.path.join(os.path.dirname(DB_PATH), "_backups")
    os.makedirs(target_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_path = os.path.join(target_dir, f"pmo_snap_{ts}.db")
    shutil.copy2(DB_PATH, target_path)
    size = os.path.getsize(target_path)
    h = hashlib.sha256()
    with open(target_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    sha = h.hexdigest()
    conn = get_conn()
    c = conn.execute(
        "INSERT INTO db_snapshots (snapshot_path, sha256, size_bytes) VALUES (?,?,?)",
        (target_path, sha, size)
    )
    sid = c.lastrowid
    conn.commit()
    conn.close()
    return {"id": sid, "path": target_path, "sha256": sha, "size_bytes": size}


def snapshot_list(limit=20):
    """Lista snapshots mais recentes primeiro."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM db_snapshots ORDER BY criado_em DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# AGREGACOES PARA DASHBOARD
# ============================================================

def activities_for_project(project, limit=500):
    """Todas atividades de um projeto, ordenadas por data desc."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM activities WHERE project LIKE ? ORDER BY date DESC, id DESC LIMIT ?",
        (f"%{project}%", limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def heatmap_data(days=90):
    """
    Retorna contagem de atividades por dia nos ultimos N dias.
    Dict {YYYY-MM-DD: count} com zeros para dias sem atividade.
    """
    from datetime import datetime, timedelta
    conn = get_conn()
    rows = conn.execute("""
        SELECT date, COUNT(*) as n FROM activities
        WHERE date >= date('now', ? || ' days')
        GROUP BY date
    """, (f"-{days}",)).fetchall()
    result = {r['date']: r['n'] for r in rows}
    conn.close()
    # Preenche zeros para dias sem atividade
    today = datetime.now().date()
    complete = {}
    for i in range(days):
        d = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        complete[d] = result.get(d, 0)
    return complete


def activities_by_month(months=6):
    """
    Atividades por mes nos ultimos N meses (inclusive atual).
    Retorna lista ordenada cronologicamente:
      [{'ym': 'YYYY-MM', 'label': 'jan'...'dez', 'count': int}]
    Preenche meses sem atividade com count=0 para manter a curva continua.
    """
    from datetime import datetime
    conn = get_conn()
    rows = conn.execute("""
        SELECT strftime('%Y-%m', date) as ym, COUNT(*) as n
        FROM activities
        WHERE date >= date('now', ? || ' months')
        GROUP BY ym
        ORDER BY ym
    """, (f"-{months}",)).fetchall()
    conn.close()
    meses_pt = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez']
    data = {r['ym']: r['n'] for r in rows}

    # Preenche gaps: todos os meses do periodo, mesmo os vazios
    now = datetime.now()
    result = []
    ym_list = []
    y, m = now.year, now.month
    for _ in range(months + 1):
        ym_list.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            m = 12; y -= 1
    ym_list.reverse()
    for ym in ym_list:
        month_num = int(ym.split('-')[1])
        result.append({
            'ym': ym,
            'label': meses_pt[month_num - 1],
            'count': data.get(ym, 0),
        })
    return result


def sessions_start_hour_distribution(days=60):
    """
    Distribuicao de horarios de inicio das sessoes (0-23) nos ultimos N dias.
    Retorna dict {hour_int: count}, com zeros para horas sem sessao.
    """
    conn = get_conn()
    rows = conn.execute("""
        SELECT CAST(strftime('%H', started_at) AS INTEGER) as hour, COUNT(*) as n
        FROM sessions
        WHERE started_at IS NOT NULL
          AND date(started_at) >= date('now', ? || ' days')
        GROUP BY hour
    """, (f"-{days}",)).fetchall()
    conn.close()
    result = {h: 0 for h in range(24)}
    for r in rows:
        result[r['hour']] = r['n']
    return result


def sessions_per_week(weeks=12):
    """
    Numero de sessoes por semana nas ultimas N semanas (lista ordenada cronologicamente).
    Cada item: {week_start: YYYY-MM-DD, count: int}.
    Semana comeca na segunda.
    """
    from datetime import datetime, timedelta
    today = datetime.now().date()
    monday_of_this_week = today - timedelta(days=today.weekday())
    conn = get_conn()
    result = []
    for i in range(weeks - 1, -1, -1):
        monday = monday_of_this_week - timedelta(days=i*7)
        sunday = monday + timedelta(days=6)
        n = conn.execute("""
            SELECT COUNT(*) as n FROM sessions
            WHERE date(started_at) BETWEEN ? AND ?
        """, (monday.strftime('%Y-%m-%d'), sunday.strftime('%Y-%m-%d'))).fetchone()['n']
        result.append({'week_start': monday.strftime('%Y-%m-%d'), 'count': n})
    conn.close()
    return result


def projects_touched_per_week(weeks=12):
    """
    Numero de projetos distintos com atividade por semana nas ultimas N semanas.
    Mede variedade vs. foco.
    """
    from datetime import datetime, timedelta
    today = datetime.now().date()
    monday_of_this_week = today - timedelta(days=today.weekday())
    conn = get_conn()
    result = []
    for i in range(weeks - 1, -1, -1):
        monday = monday_of_this_week - timedelta(days=i*7)
        sunday = monday + timedelta(days=6)
        n = conn.execute("""
            SELECT COUNT(DISTINCT project) as n FROM activities
            WHERE date BETWEEN ? AND ?
        """, (monday.strftime('%Y-%m-%d'), sunday.strftime('%Y-%m-%d'))).fetchone()['n']
        result.append({'week_start': monday.strftime('%Y-%m-%d'), 'count': n})
    conn.close()
    return result


def hours_per_day(days=60, cap_hours_per_session=16.0, cap_hours_per_day=18.0):
    """
    Horas trabalhadas por dia nos ultimos N dias.

    Soma (ended_at - started_at) das sessoes encerradas, com cap sanitario
    por sessao e por dia (sessoes deixadas abertas ou maratonas multiplas
    no mesmo dia viram lixo estatistico).
    Duracao e atribuida ao dia de started_at (aproximacao simples —
    sessoes que atravessam meia-noite contam no dia que comecaram).

    Retorna dict {YYYY-MM-DD: horas_float} com zeros para dias sem trabalho.
    """
    from datetime import datetime, timedelta
    conn = get_conn()
    rows = conn.execute("""
        SELECT date(started_at) as dia,
               (julianday(ended_at) - julianday(started_at)) * 24.0 as horas
        FROM sessions
        WHERE ended_at IS NOT NULL
          AND started_at IS NOT NULL
          AND date(started_at) >= date('now', ? || ' days')
    """, (f"-{days}",)).fetchall()
    conn.close()
    acc = {}
    for r in rows:
        h = min(r['horas'] or 0.0, cap_hours_per_session)
        if h < 0:
            h = 0.0
        acc[r['dia']] = acc.get(r['dia'], 0.0) + h
    # Cap por dia (limite humano)
    for d in acc:
        if acc[d] > cap_hours_per_day:
            acc[d] = cap_hours_per_day
    today = datetime.now().date()
    complete = {}
    for i in range(days):
        d = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        complete[d] = round(acc.get(d, 0.0), 2)
    return complete


# Stopwords pt-br basicas para themes_top
_STOPWORDS_PT = {
    'a', 'o', 'e', 'é', 'de', 'da', 'do', 'dos', 'das', 'um', 'uma', 'uns', 'umas',
    'para', 'por', 'com', 'sem', 'em', 'no', 'na', 'nos', 'nas', 'ao', 'aos',
    'que', 'se', 'ou', 'mas', 'como', 'mais', 'menos', 'ja', 'nao', 'sim',
    'foi', 'ser', 'sao', 'eh', 'ha', 'tem', 'esta', 'esse', 'essa', 'isso',
    'este', 'esta', 'isto', 'pelo', 'pela', 'pelos', 'pelas', 'seu', 'sua',
    'sobre', 'entre', 'ate', 'apos', 'antes', 'ainda', 'porque', 'quando',
    'onde', 'qual', 'quais', 'quem', 'cada', 'todos', 'todas', 'algum', 'alguma',
    'the', 'of', 'and', 'to', 'in', 'for', 'on', 'with', 'by', 'as', 'at',
    'nao', 'sem', 'foi', 'ter', 'tem', 'teve', 'teve', 'teria',
}


def themes_top(n=30, since_days=90):
    """
    Extrai palavras recorrentes dos summary de activities dos ultimos N dias.
    Retorna [{'word': str, 'freq': int, 'projects': [str,...]}, ...] ordenado por freq.
    """
    import re
    from collections import Counter, defaultdict
    conn = get_conn()
    rows = conn.execute("""
        SELECT project, summary FROM activities
        WHERE date >= date('now', ? || ' days')
    """, (f"-{since_days}",)).fetchall()
    conn.close()

    counts = Counter()
    projects_by_word = defaultdict(set)
    word_re = re.compile(r"[a-zA-ZáàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ][a-zA-ZáàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ0-9_-]{2,}")

    for r in rows:
        project = r['project']
        text = (r['summary'] or '').lower()
        for w in word_re.findall(text):
            w_clean = w.lower().strip('-_')
            if len(w_clean) < 4 or w_clean in _STOPWORDS_PT:
                continue
            counts[w_clean] += 1
            projects_by_word[w_clean].add(project)

    result = []
    for word, freq in counts.most_common(n):
        result.append({
            'word': word,
            'freq': freq,
            'projects': sorted(projects_by_word[word])[:5],
        })
    return result


# Inicializa schema ao executar diretamente
if __name__ == "__main__":
    print(init_db())
    print(json.dumps(db_stats(), indent=2))
